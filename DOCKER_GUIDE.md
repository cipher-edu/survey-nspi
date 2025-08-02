# Docker Deployment Guide

## Environment Versions

### Development Environment
```bash
# Development muhiti uchun
docker-compose -f docker-compose.dev.yml up --build

# Yoki Windows script orqali
scripts\start_dev.bat
```

**Development features:**
- Django development server
- Debug mode enabled
- Database va PgAdmin portlari ochiq
- Live code reloading

### Production Environment
```bash
# Production muhiti uchun
docker-compose up --build

# Yoki Windows script orqali  
scripts\start_prod.bat
```

**Production features:**
- Gunicorn server with optimized workers
- NGINX reverse proxy
- SSL ready configuration
- Static files served by NGINX
- Container restart policies
- Security headers

## Available Services

| Service | Development Port | Production Access | Description |
|---------|-----------------|-------------------|-------------|
| Django Web | 8000 | 80 (via NGINX) | Main application |
| PostgreSQL | 5432 | Internal only | Database |
| Redis | 6379 | Internal only | Cache & Celery broker |
| PgAdmin | 5050 | Not exposed | Database admin |
| NGINX | - | 80, 443 | Reverse proxy |

## Quick Commands

### Development
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop
docker-compose -f docker-compose.dev.yml down

# Shell access
docker-compose -f docker-compose.dev.yml exec web bash
```

### Production
```bash
# Start production environment
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Shell access
docker-compose exec web bash
```

## SSL Configuration

Production muhitida SSL sozlash uchun:

1. SSL sertifikatni oling (Let's Encrypt tavsiya etiladi)
2. `/etc/letsencrypt` papkasini to'g'ri sozlang
3. `nginx/conf.d/default.conf` da HTTPS qismini yoqing

## Environment Variables

Development va production uchun turli `.env` fayllar:
- `.env` - asosiy environment variables
- `.env.production` - production settings template

## Monitoring

Health check endpoint: `http://localhost/health/`

## Backup

Database backup olish:
```bash
docker-compose exec db pg_dump -U survey_user survey_prod_db > backup.sql
```

Database restore qilish:
```bash
docker-compose exec -T db psql -U survey_user survey_prod_db < backup.sql
```
