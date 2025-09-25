module Message::Searchable
  extend ActiveSupport::Concern

  included do
    after_create_commit  :create_in_index
    after_update_commit  :update_in_index
    after_destroy_commit :remove_from_index

    scope :search, ->(query) do
      if connection.adapter_name == 'PostgreSQL'
        # PostgreSQL: Use tsvector search
        joins("JOIN message_search_index idx ON messages.id = idx.message_id")
          .where("idx.body_tsvector @@ plainto_tsquery('english', ?)", query)
          .ordered
      else
        # SQLite: Use FTS5 match
        joins("join message_search_index idx on messages.id = idx.rowid")
          .where("idx.body match ?", query)
          .ordered
      end
    end
  end

  private
    def create_in_index
      if self.class.connection.adapter_name == 'PostgreSQL'
        execute_sql_with_binds "INSERT INTO message_search_index(message_id, body) VALUES (?, ?)", id, plain_text_body
      else
        execute_sql_with_binds "insert into message_search_index(rowid, body) values (?, ?)", id, plain_text_body
      end
    end

    def update_in_index
      if self.class.connection.adapter_name == 'PostgreSQL'
        execute_sql_with_binds "UPDATE message_search_index SET body = ? WHERE message_id = ?", plain_text_body, id
      else
        execute_sql_with_binds "update message_search_index set body = ? where rowid = ?", plain_text_body, id
      end
    end

    def remove_from_index
      if self.class.connection.adapter_name == 'PostgreSQL'
        execute_sql_with_binds "DELETE FROM message_search_index WHERE message_id = ?", id
      else
        execute_sql_with_binds "delete from message_search_index where rowid = ?", id
      end
    end

    def execute_sql_with_binds(*statement)
      self.class.connection.execute self.class.sanitize_sql(statement)
    end
end
