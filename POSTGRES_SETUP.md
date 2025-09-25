# PostgreSQL Setup for Campfire on Dokku

This guide shows how to set up Campfire with PostgreSQL instead of SQLite for production deployment.

## What Changed

- Added `pg` gem to Gemfile for production
- Updated `config/database.yml` to use PostgreSQL in production
- Added PostgreSQL client libraries to Dockerfile
- Enabled production gem group in Docker build

## Dokku PostgreSQL Setup

### 1. Install PostgreSQL Plugin (if not already installed)

```bash
# On your Dokku server
sudo dokku plugin:install https://github.com/dokku/dokku-postgres.git
```

### 2. Create PostgreSQL Service

```bash
# Create a PostgreSQL service
dokku postgres:create campfire-db

# Verify it's running
dokku postgres:list
```

### 3. Link Database to App

```bash
# Link the database to your app (this sets DATABASE_URL automatically)
dokku postgres:link campfire-db campfire

# Verify the link
dokku postgres:info campfire-db
```

### 4. Deploy with PostgreSQL

Now deploy your updated app:

```bash
# From your local repository
git add .
git commit -m "Add PostgreSQL support for production"
git push dokku main
```

### 5. Run Database Migrations

After successful deployment:

```bash
# Run Rails migrations to create tables
dokku run campfire bin/rails db:prepare

# Or if you prefer separate commands:
dokku run campfire bin/rails db:create
dokku run campfire bin/rails db:migrate
```

## Environment Variables

The PostgreSQL plugin automatically sets:
- `DATABASE_URL` - Full PostgreSQL connection string

You can verify with:
```bash
dokku config campfire
```

Should show something like:
```
DATABASE_URL: postgres://postgres:password@dokku-postgres-campfire-db:5432/campfire_db
```

## Benefits of PostgreSQL over SQLite

1. **Concurrency** - Multiple users can write simultaneously
2. **Performance** - Better for high-traffic chat applications
3. **Reliability** - ACID compliance, better crash recovery
4. **Scalability** - Can handle larger datasets and more concurrent users
5. **Features** - Full-text search, JSON columns, advanced indexing
6. **Backup/Restore** - Better tooling for database management

## Database Management Commands

```bash
# Access PostgreSQL console
dokku postgres:connect campfire-db

# Create database backup
dokku postgres:export campfire-db > backup.sql

# Restore from backup
dokku postgres:import campfire-db < backup.sql

# View database logs
dokku postgres:logs campfire-db

# Get database info
dokku postgres:info campfire-db
```

## Rails Commands with PostgreSQL

```bash
# Run Rails console with database access
dokku run campfire bin/rails console

# Check database status
dokku run campfire bin/rails db:migrate:status

# Reset database (DANGEROUS - removes all data!)
dokku run campfire bin/rails db:reset

# Seed database if you have seed data
dokku run campfire bin/rails db:seed
```

## Monitoring and Performance

```bash
# Check app performance
dokku logs campfire --tail

# Monitor database connections
dokku postgres:info campfire-db

# Check database size
dokku postgres:connect campfire-db
# Then in psql: \l+ to see database sizes
```

## Troubleshooting

### Connection Issues
If you see connection errors:
```bash
# Check if database service is running
dokku postgres:list

# Restart database service
dokku postgres:restart campfire-db

# Check app environment has DATABASE_URL
dokku config campfire
```

### Migration Issues
```bash
# Check migration status
dokku run campfire bin/rails db:migrate:status

# Run specific migration
dokku run campfire bin/rails db:migrate:up VERSION=20240101000000

# Rollback last migration
dokku run campfire bin/rails db:migrate:down VERSION=20240101000000
```

### Performance Issues
```bash
# Enable query logging (temporary)
dokku run campfire bin/rails console
# Rails.logger.level = 0  # This enables SQL query logging

# Check for slow queries in PostgreSQL
dokku postgres:connect campfire-db
# SELECT * FROM pg_stat_activity WHERE state = 'active';
```

This setup gives you a much more robust foundation for a production chat application!