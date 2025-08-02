#!/bin/bash

# Production deployment script
# Loyihani production muhitiga deploy qilish uchun

set -e

echo "Starting production deployment..."

# 1. Environment faylini tekshirish
if [ ! -f ".env.production" ]; then
    echo "ERROR: .env.production fayli topilmadi!"
    exit 1
fi

# 2. Database backup olish (agar mavjud bo'lsa)
echo "Creating database backup..."
docker-compose exec -T db pg_dump -U survey_user survey_prod_db > backup_$(date +%Y%m%d_%H%M%S).sql || true

# 3. Docker images yangilash
echo "Building Docker images..."
docker-compose build --no-cache

# 4. Konteynerlarni to'xtatish
echo "Stopping containers..."
docker-compose down

# 5. Yangi konteynerlarni ishga tushirish
echo "Starting new containers..."
docker-compose up -d

# 6. Migratsiyalarni amalga oshirish
echo "Running migrations..."
docker-compose exec web python manage.py migrate

# 7. Static fayllarni yig'ish
echo "Collecting static files..."
docker-compose exec web python manage.py collectstatic --noinput

# 8. Health check
echo "Running health check..."
sleep 10
docker-compose exec web python manage.py check

# 9. Loglarni ko'rsatish
echo "Deployment completed! Showing logs..."
docker-compose logs --tail=50
