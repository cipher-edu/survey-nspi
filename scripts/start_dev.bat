@echo off
REM Development environment uchun Docker Compose
echo Starting development environment...

REM Existing containers ni to'xtatish
docker-compose -f docker-compose.dev.yml down

REM Development containers ni ishga tushirish
docker-compose -f docker-compose.dev.yml up --build -d

REM Migratsiyalarni bajarish
docker-compose -f docker-compose.dev.yml exec web python manage.py migrate

REM Static files collect qilish
docker-compose -f docker-compose.dev.yml exec web python manage.py collectstatic --noinput

echo Development environment started!
echo Web: http://localhost:8000
echo PgAdmin: http://localhost:5050
echo.
echo Press any key to see logs...
pause
docker-compose -f docker-compose.dev.yml logs -f
