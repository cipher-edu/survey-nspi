#!/bin/bash

# Production health check script
# Serverni ishlab turganligini tekshirish uchun

set -e

echo "Checking Django health..."

# Database ulanishini tekshirish
python manage.py check --database default

# Migratsiyalar holatini tekshirish  
python manage.py showmigrations --plan | grep '\[ \]' && {
    echo "WARNING: Unapplied migrations found!"
    exit 1
} || echo "All migrations applied"

# Static fayllar mavjudligini tekshirish
python manage.py collectstatic --dry-run --noinput > /dev/null 2>&1 || {
    echo "ERROR: Static files collection failed"
    exit 1
}

# Celery worker ishlab turganligini tekshirish (agar kerak bo'lsa)
# celery -A external_auth_project status > /dev/null 2>&1 || {
#     echo "WARNING: Celery workers not running"
# }

echo "Health check passed!"
