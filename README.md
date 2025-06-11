# HEMIS So'rovnoma Tizimi 🚀

### Tashqi API bilan integratsiyalashgan dinamik so'rovnomalar platformasi

![Django](https://img.shields.io/badge/Django-4.2-blue?logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-5.3-green?logo=celery)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.x-blue?logo=tailwindcss&logoColor=white)
![Litsenziya](https://img.shields.io/badge/Litsenziya-MIT-green)

Ushbu loyiha talabalar uchun tashqi **HEMIS API** orqali autentifikatsiya qilish va ular uchun administratorlar tomonidan yaratilgan dinamik so'rovnomalarda qatnashish imkonini beruvchi veb-ilova hisoblanadi. Loyiha Django, Celery va zamonaviy frontend texnologiyalaridan unumli foydalangan.

---

## ✨ Asosiy imkoniyatlar

-   **Tashqi API orqali autentifikatsiya:** Foydalanuvchilar (talabalar) HEMIS tizimidagi login va parollari orqali tizimga kiradilar.
-   **Dinamik so'rovnoma konstruktori:** Administratorlar admin panel orqali hech qanday kod yozmasdan, turli xil savol turlari (yagona tanlov, ko'p tanlov, matnli javob) bilan so'rovnomalar yarata oladilar.
-   **Asinxron vazifalar:** Foydalanuvchi profillarini yangilash kabi sekin operatsiyalar **Celery** yordamida fonda bajariladi, bu esa tizimning tez ishlashini ta'minlaydi.
-   **Zamonaviy va Interaktiv UI/UX:** So'rovnoma sahifasi Vanilla JavaScript yordamida client-side rendering (CSR) qilinadi. Bu sahifani yangilamasdan tezkor ishlash imkonini beradi.
-   **Professional Admin Paneli:** `Jazzmin` yordamida admin paneli ancha chiroyli va funksional ko'rinishga keltirilgan.
-   **Responsiv Dizayn:** **Tailwind CSS** yordamida yaratilgan interfeys mobil qurilmalardan tortib katta ekranlargacha mukammal ko'rinadi.
-   **Xavfsiz konfiguratsiya:** Barcha maxfiy ma'lumotlar (`SECRET_KEY`, API tokenlar) koddan ajratilib, `.env` faylida saqlanadi.

---

## 🎨 Tashqi ko'rinishi

So'rovnoma sahifasi foydalanuvchi uchun maksimal darajada qulay qilib ishlangan. Progress "Stepper" yordamida ko'rsatiladi va to'liq interaktiv.

![So'rovnoma sahifasi](![image](https://github.com/user-attachments/assets/61045356-6446-46ef-9cb4-a27f4853a2cc)
)

---

## ⚙️ Texnologiyalar steki

| Kategoriya          | Texnologiya                                                                |
| ------------------- | -------------------------------------------------------------------------- |
| **Backend**         | Django, Django REST Framework, Simple JWT                                  |
| **Frontend**        | HTML5, Tailwind CSS, Vanilla JavaScript, Alpine.js (base.html da)          |
| **Ma'lumotlar Baza**| PostgreSQL (Production uchun tavsiya etiladi), SQLite3 (Development uchun)   |
| **Asinxron Vazifalar** | Celery, Redis (Broker va Natijalar uchun)                                |
| **Server**          | Gunicorn / uWSGI (Production), Nginx (Reverse Proxy)                       |

---

## 🔧 O'rnatish va sozlash

Loyihani lokal kompyuteringizda ishga tushirish uchun quyidagi qadamlarni bajaring:

**1. Loyihani yuklab oling:**
```bash
git clone https://github.com/sizning-username/sizning-repo.git
cd sizning-repo
```

**2. Virtual muhit yaratish va aktivlashtirish:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# MacOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Python bog'liqliklarini o'rnatish:**
> **Muhim:** Loyihangizda `requirements.txt` fayli bo'lishi kerak. Uni yaratish uchun: `pip freeze > requirements.txt`

```bash
pip install -r requirements.txt
```

**4. Frontend bog'liqliklarini o'rnatish:**
> Buning uchun kompyuteringizda [Node.js](https://nodejs.org/) o'rnatilgan bo'lishi kerak.

```bash
npm install
```

**5. Muhit o'zgaruvchilarini sozlash:**
`.env.example` faylidan nusxa olib, `.env` nomli yangi fayl yarating va uni o'zingizning ma'lumotlaringiz bilan to'ldiring.

```bash
cp .env.example .env
# Endi .env faylini tahrirlang
```

**6. Ma'lumotlar bazasini sozlash:**
```bash
python manage.py migrate
```

**7. Superuser (admin) yaratish:**
```bash
python manage.py createsuperuser
```

---

## 🚀 Loyihani ishga tushirish

Loyihani to'liq ishga tushirish uchun **3 ta alohida terminal** oynasi kerak bo'ladi.

**1-Terminal: Tailwind CSS kompilyatorini ishga tushirish**
(CSS'dagi o'zgarishlarni avtomatik kuzatib boradi)
```bash
npx tailwindcss -i ./auth_app/static/auth_app/css/input.css -o ./auth_app/static/auth_app/css/output.css --watch
```

**2-Terminal: Celery worker'ni ishga tushirish**
(Fon vazifalarini bajarish uchun)
```bash
celery -A external_auth_project worker -l info
```

**3-Terminal: Django serverini ishga tushirish**
```bash
python manage.py runserver
```

Endi loyiha [http://127.0.0.1:8000/](http://127.0.0.1:8000/) manzilida ishlayotgan bo'lishi kerak.

---

## 🔑 Muhit o'zgaruvchilari (`.env` fayli)

`.env` faylingiz taxminan quyidagi ko'rinishda bo'lishi kerak. **Bu faylni hech qachon Git'ga qo'shmang!**

```ini
# Django sozlamalari
DJANGO_SECRET_KEY='sizning_maxfiy_kalitingiz'
DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1, localhost

# Tashqi API sozlamalari
EXTERNAL_API_BASE_URL="https://student.nspi.uz/rest"

# Redis va Celery sozlamalari
CELERY_BROKER_URL="redis://localhost:6379/0"
CELERY_RESULT_BACKEND="redis://localhost:6379/0"
REDIS_URL="redis://localhost:6379/1" # Kesh uchun

# Tizim tokenlari (agar kerak bo'lsa)
HEMIS_SYSTEM_API_TOKEN=sizning_tizim_tokeningiz
```

---

## 📂 Loyiha strukturasi

```
├── auth_app/                # Asosiy ilova
│   ├── migrations/
│   ├── services/            # Tashqi API bilan ishlash uchun servislar
│   ├── static/              # CSS, JS fayllar
│   ├── tasks.py             # Celery vazifalari
│   ├── templates/           # HTML shablonlar
│   ├── admin.py
│   ├── models.py
│   ├── views.py
│   └── ...
├── external_auth_project/     # Loyihaning asosiy sozlamalari
│   ├── settings.py
│   ├── urls.py
│   └── celery.py
├── manage.py                # Django boshqaruv skripti
├── requirements.txt         # Python bog'liqliklari
├── package.json             # Frontend bog'liqliklari
├── tailwind.config.js       # Tailwind sozlamalari
└── README.md                # Shu fayl
```

---

## 📜 Litsenziya

Ushbu loyiha MIT litsenziyasi ostida tarqatiladi. Batafsil ma'lumot uchun `LICENSE` fayliga qarang.
