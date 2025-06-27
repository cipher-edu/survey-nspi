# 1. Rasmiy Python image (eng kichik, lekin kerakli kutubxonalar bilan)
FROM python:3.11-slim

# 2. Ishchi katalogni o‘rnatamiz
WORKDIR /app

# 3. Muhit o‘zgaruvchilar
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# 4. Tizimga kerakli kutubxonalarni o‘rnatamiz (psycopg2, mysqlclient, va h.k.)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc default-libmysqlclient-dev pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 5. Virtual muhit yaratamiz
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 6. Python kutubxonalarini o‘rnatamiz
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 7. Loyihani konteynerga ko‘chiramiz
COPY . .

# 8. Statik fayllar (kerak bo‘lsa avtomatik yig‘iladi)
# RUN python manage.py collectstatic --noinput

# 9. Cloud Run porti 8080 da ishlaydi
EXPOSE 8080

# 10. Gunicorn serverini port 8080 da ishga tushiramiz
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "external_auth_project.wsgi:application"]
