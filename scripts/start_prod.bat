@echo off
REM Production environment uchun Docker Compose
echo Starting production environment...

REM Existing containers ni to'xtatish
docker-compose down

REM Production containers ni ishga tushirish
docker-compose up --build -d

REM Migratsiyalarni bajarish
docker-compose exec web python manage.py migrate

REM Superuser yaratish (agar kerak bo'lsa)
echo Do you want to create a superuser? (y/n)
set /p create_superuser=
if /i "%create_superuser%"=="y" (
    docker-compose exec web python manage.py createsuperuser
)

REM Health check
docker-compose exec web python manage.py check --deploy

echo Production environment started!
echo Web: http://localhost (via NGINX)
echo.
echo Press any key to see logs...
pause
docker-compose logs -f
