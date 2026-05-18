# Mini-grup_12

Django REST Framework asosida yozilgan e-commerce API. Loyihada foydalanuvchi
ro'yxatdan o'tishi, JWT orqali login, mahsulotlar, kategoriyalar, savat,
buyurtmalar, yangiliklar va manzil ma'lumotlari bilan ishlash imkoniyatlari bor.

## Texnologiyalar

- Python 3.12
- Django 6
- Django REST Framework
- Simple JWT
- django-environ
- django-filter
- SQLite development uchun
- PostgreSQL production Docker compose uchun
- Gunicorn va WhiteNoise production uchun
- Docker va Docker Compose

## Loyiha Tuzilishi

```text
Mini-grup_12/
|-- cart/                  # Savat
|-- category/              # Kategoriya va xususiyatlar
|-- common/                # Region, tuman, address
|-- config/                # Django settings, urls, wsgi/asgi
|-- news/                  # Yangiliklar
|-- order/                 # Buyurtmalar va promocode
|-- product/               # Mahsulotlar va favourites
|-- users/                 # Auth, user, profile, OTP
|-- Dockerfile
|-- docker-compose.dev.yml
|-- docker-compose.prod.yml
|-- .dockerignore
|-- .env.example
`-- requirements.txt
```

## Environment

`.env.example` asosida `.env` fayl yarating.

PowerShell:

```powershell
Copy-Item .env.example .env
```

Asosiy env qiymatlar:

```env
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000
DATABASE_URL=
```

Production uchun muhim qiymatlar:

```env
SECRET_KEY=strong-production-secret
DEBUG=False
ALLOWED_HOSTS=example.com,www.example.com
CSRF_TRUSTED_ORIGINS=https://example.com
POSTGRES_PASSWORD=strong-postgres-password
```

## Local Ishga Tushirish

Virtual environment aktiv qiling:

```powershell
venv\Scripts\Activate.ps1
```

Dependencylarni o'rnating:

```powershell
pip install -r requirements.txt
```

Migrationlarni bajaring:

```powershell
python manage.py migrate
```

Serverni ishga tushiring:

```powershell
python manage.py runserver
```

API manzili:

```text
http://127.0.0.1:8000/
```

Admin panel:

```text
http://127.0.0.1:8000/admin/
```

## Docker Development

Development compose Django `runserver` bilan ishlaydi va lokal kodni container
ichiga volume qilib ulaydi.

```bash
docker compose -f docker-compose.dev.yml up --build
```

To'xtatish:

```bash
docker compose -f docker-compose.dev.yml down
```

## Docker Production

Production compose PostgreSQL, Gunicorn va static/media volume bilan ishlaydi.

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

Loglarni ko'rish:

```bash
docker compose -f docker-compose.prod.yml logs -f web
```

To'xtatish:

```bash
docker compose -f docker-compose.prod.yml down
```

Production container ichida migration va static yig'ish avtomatik bajariladi:

```text
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn config.wsgi:application
```

## API Yo'llari

Base URL:

```text
http://127.0.0.1:8000
```

Auth va user:

| Method | Endpoint | Tavsif |
| --- | --- | --- |
| POST | `/api/user/api/v1/auth/register/` | Ro'yxatdan o'tish va OTP yuborish |
| POST | `/api/user/api/v1/auth/resend-otp/` | OTP qayta yuborish |
| POST | `/api/user/api/v1/auth/verify/` | OTP tasdiqlash va token olish |
| POST | `/api/user/api/v1/auth/token/` | JWT token olish |
| POST | `/api/user/api/v1/auth/token/refresh/` | Refresh token |
| GET | `/api/user/api/v1/user/me/` | Joriy user ma'lumoti |
| GET/PATCH/DELETE | `/api/user/api/v1/user/profile/` | User profile |

Product:

| Method | Endpoint | Tavsif |
| --- | --- | --- |
| GET/POST | `/api/product/api/v1/products/` | Mahsulotlar ro'yxati yoki yaratish |
| GET/PUT/PATCH/DELETE | `/api/product/api/v1/products/{id}/` | Mahsulot detail |
| GET/POST | `/api/product/api/v1/favourites/` | Favourite ro'yxati yoki qo'shish |
| DELETE | `/api/product/api/v1/favourites/{id}/` | Favourite o'chirish |

Category:

| Method | Endpoint | Tavsif |
| --- | --- | --- |
| GET/POST | `/api/category/api/v1/categories/` | Kategoriyalar |
| GET/POST | `/api/category/api/v1/properties/` | Kategoriya xususiyatlari |
| GET/POST | `/api/category/api/v1/options/` | Xususiyat optionlari |

Cart:

| Method | Endpoint | Tavsif |
| --- | --- | --- |
| GET | `/api/card/my/` | Mening savatim |
| POST | `/api/card/add/` | Savatga mahsulot qo'shish |
| PATCH | `/api/card/update/` | Savatdagi miqdorni o'zgartirish |
| DELETE | `/api/card/remove/` | Savatdan mahsulot o'chirish |

Order:

| Method | Endpoint | Tavsif |
| --- | --- | --- |
| GET | `/api/order/orders/` | Buyurtmalar ro'yxati |
| POST | `/api/order/orders/create/` | Checkout |
| GET/PUT/PATCH/DELETE | `/api/order/orders/{uuid}/` | Buyurtma detail |
| POST | `/api/order/orders/{uuid}/add-item/` | Buyurtmaga item qo'shish |
| POST | `/api/order/orders/{uuid}/apply-promo/` | Promocode qo'llash |
| POST | `/api/order/orders/{uuid}/cancel/` | Buyurtmani bekor qilish |
| GET | `/api/order/orders/my-orders/` | Mening buyurtmalarim |

Common va news:

| Method | Endpoint | Tavsif |
| --- | --- | --- |
| GET/POST | `/api/common/region/` | Regionlar |
| GET/POST | `/api/common/district/` | Tumanlar |
| GET/POST | `/api/common/address/` | User address |
| GET/POST | `/api/news/news/` | Yangiliklar |

## Foydali Komandalar

Django check:

```powershell
python manage.py check
```

Migration yaratish:

```powershell
python manage.py makemigrations
```

Migration bajarish:

```powershell
python manage.py migrate
```

Superuser yaratish:

```powershell
python manage.py createsuperuser
```

Static fayllarni yig'ish:

```powershell
python manage.py collectstatic --noinput
```

## Eslatma

- Development holatda SQLite ishlaydi.
- Production Docker compose holatda PostgreSQL ishlaydi.
- Auth talab qiladigan endpointlarda header yuboriladi:

```http
Authorization: Bearer <access_token>
```
