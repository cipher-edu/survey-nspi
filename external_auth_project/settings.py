from pathlib import Path
import environ # environ ni import qilish
import os
import logging

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

# environs sozlamalari
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, True) # Agar .env da bo'lmasa, False bo'ladi
)
# .env faylini o'qish (agar mavjud bo'lsa)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-test-key-for-development-only')
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'
# Production uchun aniq hostlarni belgilash
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition

INSTALLED_APPS = [
    'jazzmin',  # Admin interfeysini yaxshilash uchun
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_results',
    'auth_app',  
    'rest_framework',
    'rest_framework_simplejwt',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', # Sessiyalar uchun zarur
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,  # Disable token rotation
    'BLACKLIST_AFTER_ROTATION': False,  # Disable blacklisting
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/' 
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Additional locations of static files for development
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_DIR = BASE_DIR / 'media'
MEDIA_ROOT = MEDIA_DIR
MEDIA_URL = '/media/'
# Xavfsizlik sozlamalari
# Production uchun HTTPS va CSRF sozlamalari
X_FRAME_OPTIONS = 'DENY' 
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Production uchun HTTPS sozlamalari (HTTPS dan foydalanayotgan bo'lsangiz)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 yil
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# CSRF himoyasi
CSRF_COOKIE_HTTPONLY = True  # CSRF cookie'sini JavaScript orqali o'qish mumkin emas
CSRF_COOKIE_AGE = 60 * 60 * 24  # CSRF cookie muddati (1 kun)
CSRF_COOKIE_PATH = '/'  # CSRF cookie'si barcha URL'lar uchun amal qiladi
CSRF_COOKIE_DOMAIN = None  # Agar subdomenlar uchun kerak bo'lsa, domen nomini qo'shing
# settings.py
CSRF_COOKIE_NAME = 'hemis_csrf_token'  # CSRF cookie nomi
CSRF_USE_SESSIONS = False  # CSRF token sessiyada saqlanmaydi, faqat cookie'da
CSRF_COOKIE_SAMESITE = 'Lax' # Yoki 'Strict' (ko'proq himoya, lekin ba'zi holatlarda noqulaylik tug'dirishi mumkin)
# CSRF_TRUSTED_ORIGINS = ['https://survey.nspi.uz']

ROOT_URLCONF = 'external_auth_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Template directory
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ...
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://redis:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://redis:6379/0')

# Use database cache instead of Redis for development
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "cache_table",
    }
}

# Use database sessions instead of cache-based sessions
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# API sozlamalari
EXTERNAL_API_BASE_URL = env('EXTERNAL_API_BASE_URL', default="https://student.nspi.uz/rest")
EXTERNAL_API_LOGIN_ENDPOINT = f"{EXTERNAL_API_BASE_URL}/v1/auth/login"
EXTERNAL_API_ACCOUNT_ME_ENDPOINT = f"{EXTERNAL_API_BASE_URL}/v1/account/me"
EXTERNAL_API_REFRESH_TOKEN_ENDPOINT = f"{EXTERNAL_API_BASE_URL}/v1/auth/refresh-token" # Yangi
REQUESTS_VERIFY_SSL = env.bool('REQUESTS_VERIFY_SSL', default=True)
# ...


# external_auth_project/settings.py
# ...
API_TOKEN_REFRESH_THRESHOLD_SECONDS = 10 * 60 # Token muddati tugashiga 10 daqiqa qolganda yangilash (default 5 edi)

# Admin panelidagi action uchun yoki tizimli tasklar uchun ishlatiladigan token (agar mavjud bo'lsa)
HEMIS_ADMIN_API_TOKEN = env('b1scfqAQKK2PjRvll0MTAbFOQ1yumi4b', default=None) 
# Yoki HEMIS_SYSTEM_API_TOKEN (tasks.py da ishlatilgan)
HEMIS_SYSTEM_API_TOKEN = env('HEMIS_SYSTEM_API_TOKEN', default=None)

# API logout endpointi (agar mavjud bo'lsa)
EXTERNAL_API_LOGOUT_ENDPOINT = env('EXTERNAL_API_LOGOUT_ENDPOINT', default=None) # Masalan: f"{EXTERNAL_API_BASE_URL}/v1/auth/logout"

# Dashboardda profilni avtomatik yangilash intervali (daqiqa)
# DASHBOARD_PROFILE_REFRESH_INTERVAL_MINUTES = env.int('DASHBOARD_PROFILE_REFRESH_INTERVAL_MINUTES', default=30)
# ...
WSGI_APPLICATION = 'external_auth_project.wsgi.application'

LOGIN_URL = 'login'  # URL for login view
LOGIN_REDIRECT_URL = 'home'  # URL to redirect after login
# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': env('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': env('DB_NAME', default='survey_prod_db'),
        'USER': env('DB_USER', default='survey_user'),
        'PASSWORD': env('DB_PASSWORD', default='your_local_password'),  # <-- bu to'g'ri bo'lishi kerak
        'HOST': env('DB_HOST', default='db'),
        'PORT': env('DB_PORT', default='5432'),
    }
}


# DATABASES = {
#     'default': {
#         'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
#         'NAME': os.getenv('DB_NAME', BASE_DIR / 'db.sqlite3'), # Agar sqlite bo'lsa, fallback
#         'USER': os.getenv('DB_USER'), # MySQL uchun None bo'lmasligi kerak
#         'PASSWORD': os.getenv('DB_PASSWORD'), # MySQL uchun None bo'lmasligi kerak
#         'HOST': os.getenv('DB_HOST', 'localhost'),
#         'PORT': os.getenv('DB_PORT', '3306'), # MySQL uchun default port
#     }
# }

# Agar DB_ENGINE sqlite bo'lsa, USER, PASSWORD, HOST, PORT kerak emas. Buni tekshirish mumkin:
if DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
    # SQLite uchun kerakmas maydonlarni olib tashlash
    DATABASES['default'].pop('USER', None)
    DATABASES['default'].pop('PASSWORD', None)
    DATABASES['default'].pop('HOST', None)
    DATABASES['default'].pop('PORT', None)
elif DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
    # MySQL uchun qo'shimcha sozlamalar (ixtiyoriy)
    DATABASES['default'].setdefault('OPTIONS', {
        'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        'charset': 'utf8mb4', # Yaxshi UTF-8 qo'llab-quvvatlashi uchun
    })
    # MySQL uchun portni int ga o'tkazish
    if DATABASES['default'].get('PORT'):
        try:
            DATABASES['default']['PORT'] = int(DATABASES['default']['PORT'])
        except ValueError:
            logger.warning(f"DB_PORT qiymati ({DATABASES['default']['PORT']}) raqam emas. MySQL uchun standart port ishlatiladi yoki xatolik yuz berishi mumkin.")
            DATABASES['default']['PORT'] = '3306' # Fallback yoki xatolikni oldini olish


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'ciphered_api',
#         'USER': 'ciphered_kor',
#         'PASSWORD': '16172714Oo.',
#         'HOST':'localhost',
#         'PORT':'3306',
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# external_auth_project/settings.py

# ... (boshqa sozlamalar) ...

# Sessiya muddati (masalan, 1 kun)
SESSION_COOKIE_AGE = 24 * 60 * 60  # 1 kun sekundlarda

# Logging sozlamalari (muammolarni kuzatish uchun juda muhim)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO' if not DEBUG else 'DEBUG',  # Production uchun INFO
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': { # Faylga yozish uchun (productionda foydali)
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'django_app.log', # Loyiha papkasida log fayli
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,  # Ko'proq backup fayllar
            'formatter': 'verbose',
        },
        'error_file': {  # Faqat xatoliklar uchun alohida fayl
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'django_error.log',
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'auth_app': { # Bizning ilovamiz uchun logger
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO' if not DEBUG else 'DEBUG',
            'propagate': False,
        },
         # requests kutubxonasi loglarini kamaytirish uchun (kerak bo'lsa)
        'requests': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'urllib3': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
    'root': { # Boshqa barcha loggerlar uchun
        'handlers': ['console', 'file', 'error_file'],
        'level': 'INFO',
    }
}
