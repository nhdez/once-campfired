# Deploying Once Campfire with Dokku

This guide shows how to deploy Campfire using Dokku instead of plain Docker.

## Prerequisites

- Dokku server set up and running
- Domain name pointing to your Dokku server
- SSH access to your Dokku server

## 1. Create the Dokku App

```bash
# On your Dokku server
dokku apps:create campfire
```

## 2. Configure Environment Variables

```bash
# Required: Generate a secret key
dokku config:set campfire SECRET_KEY_BASE=$(openssl rand -hex 64)

# Optional: Enable SSL with Let's Encrypt
dokku config:set campfire SSL_DOMAIN=chat.yourdomain.com

# Alternative: Disable SSL for HTTP-only deployment
dokku config:set campfire DISABLE_SSL=true

# Optional: Web Push notifications (generate with /script/admin/create-vapid-key)
dokku config:set campfire VAPID_PUBLIC_KEY=your_public_key
dokku config:set campfire VAPID_PRIVATE_KEY=your_private_key

# Optional: Error reporting
dokku config:set campfire SENTRY_DSN=your_sentry_dsn

# Production Rails environment
dokku config:set campfire RAILS_ENV=production
```

## 3. Set Up Persistent Storage

```bash
# Create a directory for persistent data
dokku storage:ensure-directory campfire-storage

# Mount storage for database and file attachments
dokku storage:mount campfire /var/lib/dokku/data/storage/campfire-storage:/rails/storage
```

## 4. Configure Domain and SSL

```bash
# Set your domain
dokku domains:set campfire chat.yourdomain.com

# Enable Let's Encrypt (if using SSL_DOMAIN)
dokku letsencrypt:enable campfire
```

## 5. Deploy from Git

### Option A: Deploy from GitHub (recommended)

```bash
# Add dokku remote to your local repo
git remote add dokku dokku@your-server.com:campfire

# Push to deploy
git push dokku main
```

### Option B: Deploy from Docker Hub

If you want to build and push to a registry first:

```bash
# Build and tag locally
docker build -t your-registry/campfire .
docker push your-registry/campfire

# Deploy from registry
dokku git:from-image campfire your-registry/campfire:latest
```

## 6. Configure Ports (if needed)

Campfire exposes ports 80 and 443, but Dokku typically handles this automatically:

```bash
# Check port configuration
dokku ports:list campfire

# If needed, manually configure ports
dokku ports:add campfire http:80:80
dokku ports:add campfire https:443:443
```

## 7. Post-Deployment

After deployment, your app will be available at your configured domain.

### First-time setup:
1. Visit your Campfire URL
2. You'll be guided through creating an admin account
3. The admin email will be shown on the login page for password resets

### Monitoring:
```bash
# Check app logs
dokku logs campfire

# Check running processes
dokku ps:report campfire

# Restart if needed
dokku ps:restart campfire
```

## Key Differences from Docker Deployment

| Docker | Dokku |
|--------|--------|
| Manual port mapping (`--publish 80:80 443:443`) | Automatic port mapping |
| Manual volume management (`--volume`) | `dokku storage:mount` |
| Manual environment variables (`--env`) | `dokku config:set` |
| Manual SSL setup | Built-in Let's Encrypt support |
| Manual container management | Automatic restarts and health checks |

## Environment Variables Reference

### Required
- `SECRET_KEY_BASE` - Rails secret key for encryption

### SSL Configuration (choose one)
- `SSL_DOMAIN=chat.example.com` - Enable Let's Encrypt SSL
- `DISABLE_SSL=true` - Serve over HTTP only

### Optional Features
- `VAPID_PUBLIC_KEY` / `VAPID_PRIVATE_KEY` - Web Push notifications
- `SENTRY_DSN` - Error reporting to Sentry
- `RAILS_MASTER_KEY` - Alternative to SECRET_KEY_BASE for encrypted credentials

### System Configuration
- `RAILS_ENV=production` - Rails environment (auto-set by Dokku)
- `PORT` - Application port (auto-set by Dokku)

## Troubleshooting

### App won't start
```bash
# Check logs for errors
dokku logs campfire --tail

# Verify environment variables
dokku config campfire
```

### Database issues
```bash
# Run Rails commands
dokku run campfire bin/rails db:migrate
dokku run campfire bin/rails console
```

### SSL issues
```bash
# Check Let's Encrypt status
dokku letsencrypt:list

# Renew SSL certificate
dokku letsencrypt:renew campfire
```

### Storage issues
```bash
# Check mounted storage
dokku storage:list campfire

# Verify directory exists and has correct permissions
ls -la /var/lib/dokku/data/storage/campfire-storage
```

## Updating Campfire

```bash
# Pull latest changes
git pull origin main

# Deploy update
git push dokku main

# Run any new migrations (if needed)
dokku run campfire bin/rails db:migrate
```

## Advantages of Dokku Deployment

1. **Simplified Management** - One command deployment and updates
2. **Built-in SSL** - Automatic Let's Encrypt certificates
3. **Zero-downtime Deploys** - Rolling deployments
4. **Health Checks** - Automatic restart on failure
5. **Log Management** - Centralized logging with `dokku logs`
6. **Scaling** - Easy horizontal scaling if needed
7. **Backup Integration** - Easy to backup with Dokku plugins

This approach is much more maintainable than managing raw Docker containers!