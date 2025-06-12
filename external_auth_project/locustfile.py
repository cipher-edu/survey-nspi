import random
from locust import HttpUser, task, between, events
from locust.exception import StopUser
import logging

# --- SOZLAMALAR ---
# Test uchun ishlatiladigan foydalanuvchilar ro'yxati.
# Eng yaxshi usul - bu ma'lumotlarni alohida fayldan o'qish, lekin hozircha shu yerda.
TEST_USERS = [
    {"username": "testuser1", "password": "password123"},
    {"username": "testuser2", "password": "password123"},
    {"username": "testuser3", "password": "password123"},
    # ... ko'proq foydalanuvchi qo'shing ...
]

if not TEST_USERS:
    logging.error("TEST_USERS ro'yxati bo'sh. Test uchun kamida bitta foydalanuvchi kiriting.")
    exit(1)


class SurveyUser(HttpUser):
    """
    So'rovnoma tizimini test qiluvchi virtual foydalanuvchi.
    Har bir foydalanuvchi:
    1. Tizimga kiradi (login).
    2. Barcha so'rovnomalar ro'yxatini oladi.
    3. Tasodifiy so'rovnomani tanlab, unga javob yuboradi.
    """
    
    # MUHIM: Xatolikni tuzatish uchun Django serveringiz manzilini ko'rsating
    host = "http://127.0.0.1:8000"
    
    # Har bir so'rov orasida 1-3 soniya kutish
    wait_time = between(1, 3)

# locustfile.py

def on_start(self):
    """Har bir virtual foydalanuvchi ishni boshlashidan oldin bir marta chaqiriladi."""
    
    # ... (creds = random.choice(TEST_USERS) qismi o'zgarishsiz)
    creds = random.choice(TEST_USERS)
    
    # 1. Login sahifasiga GET so'rov yuborib, CSRF tokenini olish
    self.client.get("/login/", name="/login [GET]")
    
    # CSRF cookie nomini aniqlash (settings.py ga qarab)
    csrf_cookie_name = "hemis_csrf_token"  # Yoki sizning sozlamangizdagi nom
    
    # O'zgartirilgan tekshiruv
    if csrf_cookie_name not in self.client.cookies:
        logging.error(f"Login sahifasidan '{csrf_cookie_name}' nomli CSRF token olinmadi. Cookie'lar: {self.client.cookies}")
        raise StopUser("CSRF token topilmadi.")
        
    csrf_token = self.client.cookies[csrf_cookie_name]

    # 2. Tizimga kirish (login)
    res = self.client.post(
        "/login/",
        data={
            "username": creds["username"],
            "password": creds["password"],
            "csrfmiddlewaretoken": csrf_token  # CSRF tokenini form data bilan birga yuborish
        },
        name="/login [POST]"
    )
    
    # Login muvaffaqiyatli bo'lmaganini tekshirish
    if res.status_code != 302: # Muvaffaqiyatli login odatda 302 Redirect qaytaradi
        logging.error(f"Foydalanuvchi '{creds['username']}' tizimga kira olmadi. Status: {res.status_code}, URL: {res.url}, Matn: {res.text[:200]}")
        raise StopUser("Login muvaffaqiyatsiz.")
    
    # ... (qolgan qism o'zgarishsiz)
    else:
                logging.error(f"Aktiv so'rovnomalarni olib bo'lmadi. Status: {response.status_code}")
                self.survey_ids = []

    @task
    def view_and_submit_random_survey(self):
        """
        Asosiy vazifa: tasodifiy so'rovnomani ko'rish va unga javob yuborish.
        """
        if not self.survey_ids:
            # Agar aktiv so'rovnomalar bo'lmasa, bu vazifani o'tkazib yuborish
            self.interrupt(reschedule=False)
            return

        # 1. Tasodifiy so'rovnoma ID sini tanlash
        survey_pk = random.choice(self.survey_ids)

        # 2. So'rovnoma sahifasini "ochish" (ma'lumotlarni olish)
        # Bu bizning CSR client-side rendering yondashuvimizga mos keladi
        with self.client.get(f"/surveys/{survey_pk}/", name="/surveys/[pk]") as response:
            if response.status_code != 200:
                return # Agar sahifa ochilmasa, davom etmaymiz

        # 3. Soxta javoblarni generatsiya qilish (real testda bu yanada murakkab bo'lishi mumkin)
        # Hozircha barcha savollarga oddiy matnli javob beramiz
        # Bu qismni API'dan olingan savol turlariga qarab moslashtirish kerak
        answers_payload = {
            "answers": {
                "1": "Locust test javobi",  # Savol ID: Javob
                "2": ["1", "3"],          # Ko'p tanlovli savol uchun
                "3": "5"                  # Yagona tanlovli savol uchun
                # ... haqiqiy savol ID'larini bu yerga qo'yish kerak
            }
        }
        
        # 4. Javoblarni API ga yuborish
        # CSRF tokenini headerni ichiga qo'shish
        headers = {'X-CSRFToken': self.client.cookies.get('csrftoken', '')}
        self.client.post(
            f"/api/surveys/{survey_pk}/submit/",
            json=answers_payload,
            headers=headers,
            name="/api/surveys/[pk]/submit/"
        )

# --- Yangi API endpoint qo'shish kerak ---
# `auth_app/views.py` ga so'rovnomalarni olish uchun kichik API endpoint qo'shing.
# Bu Locust'ning har safar HTML'ni parse qilishidan ko'ra ancha samarali.

# `auth_app/views.py` ga qo'shing:
#
# from django.http import JsonResponse
# from .models import Survey
#
# def get_active_surveys_api(request):
#     survey_ids = list(Survey.objects.filter(is_active=True).values_list('id', flat=True))
#     return JsonResponse({"survey_ids": survey_ids})
#
# `auth_app/urls.py` ga qo'shing:
#
# path('api/active_surveys/', views.get_active_surveys_api, name='active_surveys_api'),