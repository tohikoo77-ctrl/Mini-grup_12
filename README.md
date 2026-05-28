# Mini-grup_12

Django REST Framework asosida yozilgan e-commerce API. Loyihada user ro'yxatdan
o'tishi, OTP verification, JWT auth, mahsulotlar, kategoriyalar, favourites,
savat, checkout, order, promocode, region/district/address va news bilan ishlash
imkoniyatlari bor.

## Texnologiyalar

- Python 3.12+
- Django 6.0.4
- Django REST Framework
- Simple JWT
- drf-spectacular Swagger/OpenAPI
- django-environ
- django-filter
- SQLite development uchun
- PostgreSQL Docker production uchun
- WhiteNoise va Gunicorn
- Docker / Docker Compose

## Loyiha Tuzilishi

```text
Mini-grup_12/
|-- api/                   # Home page aggregate API
|-- cart/                  # Savat va cart checkout
|-- category/              # Kategoriya, property, option
|-- common/                # Region, district, address
|-- config/                # Django settings, urls, wsgi/asgi
|-- news/                  # News read API
|-- order/                 # Order, order item, promocode
|-- product/               # Product va favourite
|-- users/                 # Auth, user, profile, OTP
|-- media/                 # Uploaded files
|-- Dockerfile
|-- docker-compose.dev.yml
|-- docker-compose.prod.yml
|-- .env.example
|-- manage.py
`-- requirements.txt
```

## Environment

`.env.example` asosida `.env` yarating:

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
POSTGRES_PASSWORD=change-me
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@example.com
```

Email OTP development holatda console backend bilan server terminaliga chiqadi.
Haqiqiy Gmail SMTP uchun `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=yourgmail@gmail.com
EMAIL_HOST_PASSWORD=google_app_password
DEFAULT_FROM_EMAIL=yourgmail@gmail.com
```

`EMAIL_HOST_PASSWORD` oddiy Gmail parol emas, Google App Password bo'lishi kerak.

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

Manzillar:

```text
API:      http://127.0.0.1:8000/
Admin:    http://127.0.0.1:8000/admin/
Swagger:  http://127.0.0.1:8000/api/docs/
Schema:   http://127.0.0.1:8000/api/schema/
```

## Docker

Development:

```bash
docker compose -f docker-compose.dev.yml up --build
docker compose -f docker-compose.dev.yml down
```

Production:

```bash
docker compose -f docker-compose.prod.yml up --build -d
docker compose -f docker-compose.prod.yml logs -f web
docker compose -f docker-compose.prod.yml down
```

Production container ichida migration, static yig'ish va gunicorn ishga tushishi
Dockerfile/compose orqali bajariladi.

## Postman

Base URL:

```text
{{url}} = http://127.0.0.1:8000
```

JWT kerak endpointlarda header:

```http
Authorization: Bearer <access_token>
```

UUID ishlatiladigan joylarda `{id}`, `{uuid}`, `{product_id}`, `{profile_id}`,
`{order_id}` haqiqiy UUID bo'lishi kerak.

## API Yo'llari

### Home

| Method | Endpoint | Auth | Tavsif |
| --- | --- | --- | --- |
| GET | `/api/home/` | No | Bosh sahifa uchun categories, news, popular products, new products |

### Auth

| Method | Endpoint | Auth | Tavsif |
| --- | --- | --- | --- |
| POST | `/api/user/api/v1/auth/register/` | No | User register, profile yaratish, OTP yuborish |
| POST | `/api/user/api/v1/auth/send-otp/` | No | Telefon raqamga OTP yuborish |
| POST | `/api/user/api/v1/auth/resend-otp/` | No | OTP qayta yuborish |
| POST | `/api/user/api/v1/auth/verify/` | No | OTP tasdiqlash, access/refresh token olish |
| POST | `/api/user/api/v1/auth/token/` | No | JWT token olish |
| POST | `/api/user/api/v1/auth/token/refresh/` | No | Refresh token orqali access yangilash |

Register body:

```json
{
  "phone_number": "+998901234567",
  "gmail": "user@gmail.com",
  "first_name": "Ali",
  "last_name": "Valiyev",
  "gender": "MALE",
  "birth_date": "2008-10-01",
  "bio": "bio text"
}
```

Send/resend OTP body:

```json
{
  "phone_number": "+998901234567"
}
```

Verify body:

```json
{
  "phone_number": "+998901234567",
  "otp_code": "123456"
}
```

`otp` fieldi ham qabul qilinadi:

```json
{
  "phone_number": "+998901234567",
  "otp": "123456"
}
```

JWT token body:

```json
{
  "phone_number": "+998901234567",
  "password": "password"
}
```

### User va Profile

| Method | Endpoint | Auth | Tavsif |
| --- | --- | --- | --- |
| GET | `/api/user/api/v1/user/` | Yes | Barcha userlar |
| GET | `/api/user/api/v1/user/{user_id}/` | Yes | User detail |
| GET | `/api/user/api/v1/user/me/` | Yes | Joriy user |
| GET | `/api/user/api/v1/user/profile/` | Yes | Barcha profilelar |
| POST | `/api/user/api/v1/user/profile/` | No | Register alias |
| POST | `/api/user/api/v1/user/profile/register/` | No | Register alias |
| GET | `/api/user/api/v1/user/profile/{profile_id}/` | Yes | Profile detail |
| PATCH | `/api/user/api/v1/user/profile/{profile_id}/` | Yes | Profile update |
| DELETE | `/api/user/api/v1/user/profile/{profile_id}/` | Yes | Profile va userni o'chirish |

Duplicate validation:

```json
{
  "phone_number": ["bu raqam mavjut."]
}
```

```json
{
  "gmail": ["bu gmail mavjut."]
}
```

Noto'g'ri yoki topilmagan id:

```json
{
  "detail": "bunday id mavjut emas."
}
```

### Product

| Method | Endpoint | Auth | Tavsif |
| --- | --- | --- | --- |
| GET | `/api/product/api/v1/products/` | No | Product list |
| GET | `/api/product/api/v1/products/{product_id}/` | No | Product detail, views +1 |
| DELETE | `/api/product/api/v1/products/{product_id}/` | No | Product o'chirish |
| GET | `/api/product/api/v1/favourites/` | Yes | Mening favourites |
| POST | `/api/product/api/v1/favourites/` | Yes | Favourite qo'shish |
| DELETE | `/api/product/api/v1/favourites/{id}/` | Yes | Favourite o'chirish |

Product filter query paramlari:

```text
?id=<uuid>
?search=iphone
?category=<uuid>
?seller=<uuid>
?min_price=100
?max_price=1000
?is_available=true
?inpk=uuid1,uuid2
```

Favourite create body:

```json
{
  "product_id": "product-uuid"
}
```

### Category

| Method | Endpoint | Auth | Tavsif |
| --- | --- | --- | --- |
| GET/POST | `/api/category/api/v1/categories/` | No | Category list/create |
| GET/PUT/PATCH/DELETE | `/api/category/api/v1/categories/{id}/` | No | Category detail/update/delete |
| GET/POST | `/api/category/api/v1/properties/` | No | Category property list/create |
| GET/PUT/PATCH/DELETE | `/api/category/api/v1/properties/{id}/` | No | Property detail/update/delete |
| GET/POST | `/api/category/api/v1/options/` | No | Property option list/create |
| GET/PUT/PATCH/DELETE | `/api/category/api/v1/options/{id}/` | No | Option detail/update/delete |

Category filterlar:

```text
?search=phone
?id=<uuid>
?in_pk=uuid1,uuid2
```

Category create body:

```json
{
  "name": "Telefonlar",
  "parent": null,
  "icon": "phone",
  "is_active": true,
  "is_deleted": false,
  "order": 1
}
```

Property create body:

```json
{
  "category": "category-uuid",
  "name": "Rang",
  "field_type": "dropdown",
  "is_required": true,
  "order": 1
}
```

Option create body:

```json
{
  "property": "property-uuid",
  "value": "Qora"
}
```

### Cart

| Method | Endpoint | Auth | Tavsif |
| --- | --- | --- | --- |
| GET | `/api/card/my/` | Yes | Mening savatim, yo'q bo'lsa yaratadi |
| POST | `/api/card/add/` | Yes | Savatga product qo'shish |
| PATCH | `/api/card/update/` | Yes | Savatdagi product quantity update |
| DELETE | `/api/card/remove/` | Yes | Savatdan product o'chirish |
| DELETE | `/api/card/clear/` | Yes | Savatni tozalash |
| POST | `/api/card/checkout/` | Yes | Savatdan order yaratish va savatni bo'shatish |

Cart add body:

```json
{
  "product_id": "product-uuid",
  "quantity": 2
}
```

Cart update body:

```json
{
  "product_id": "product-uuid",
  "quantity": 5
}
```

Cart remove body:

```json
{
  "product_id": "product-uuid"
}
```

Cart checkout body:

```json
{
  "phone": "+998901234567",
  "address": {
    "region": "Toshkent",
    "district": "Chilonzor",
    "address_line": "Bunyodkor street"
  }
}
```

`shipping_address_snapshot` ham qabul qilinadi:

```json
{
  "phone": "+998901234567",
  "shipping_address_snapshot": {
    "region": "Toshkent",
    "district": "Chilonzor",
    "address_line": "Bunyodkor street"
  }
}
```

Cart hisob-kitobi:

- `price_snapshot` savatga qo'shilgan paytdagi narxni saqlaydi.
- `subtotal` va `total_price` Decimal bilan hisoblanadi.
- Product qayta qo'shilsa quantity oshadi.
- Faqat `is_active=True` va `is_available=True` product qo'shiladi.

### Order

| Method | Endpoint | Auth | Tavsif |
| --- | --- | --- | --- |
| GET | `/api/order/orders/` | Yes | Mening orderlarim |
| POST | `/api/order/orders/create/` | Yes | `checkout_id` orqali orderni qaytarish/tasdiqlash |
| GET | `/api/order/orders/{order_id}/` | Yes | Order detail |
| PUT/PATCH | `/api/order/orders/{order_id}/` | Yes | Order phone/address update |
| DELETE | `/api/order/orders/{order_id}/` | Yes | Order o'chirish |
| POST | `/api/order/orders/{order_id}/add-item/` | Yes | Orderga product qo'shish |
| POST | `/api/order/orders/{order_id}/apply-promo/` | Yes | Promocode qo'llash |
| POST | `/api/order/orders/{order_id}/cancel/` | Yes | Order cancel |
| GET | `/api/order/orders/my-orders/` | Yes | Mening orderlarim alias |

Recommended checkout flow:

```text
1. POST /api/card/add/
2. POST /api/card/checkout/
3. GET /api/order/orders/
```

Order create body (`/api/order/orders/create/`):

```json
{
  "checkout_id": "order-uuid"
}
```

Order update body:

```json
{
  "phone": "+998901234567",
  "address": {
    "region": "Toshkent",
    "district": "Chilonzor",
    "address_line": "Bunyodkor street"
  }
}
```

Order add item body:

```json
{
  "product_id": "product-uuid",
  "quantity": 2
}
```

Apply promo body:

```json
{
  "code": "barsa2025"
}
```

Order filter query paramlari:

```text
?search=+99890
?id=<uuid>
?status=pending
?inpk=uuid1,uuid2
```

Order hisob-kitobi:

- `subtotal` order itemlar yig'indisi.
- `discount_percent` faqat valid promocode bo'lsa ishlaydi.
- `discount_amount` subtotaldan katta bo'lmaydi.
- `total_price` manfiy bo'lmaydi.
- Promocode `discount_percent` qiymati 1 dan 100 gacha bo'lishi kerak.
- `pending` va `processing` statusdagi order o'zgartiriladi.
- `shipped`, `delivered`, `cancelled` order cancel qilinmaydi.

Order status qiymatlari:

```text
pending
processing
shipped
delivered
cancelled
```

### Common

| Method | Endpoint | Auth | Tavsif |
| --- | --- | --- | --- |
| GET/POST | `/api/common/region/` | No | Region list/create |
| GET/PUT/PATCH/DELETE | `/api/common/region/{id}/` | No | Region detail/update/delete |
| GET/POST | `/api/common/district/` | No | District list/create |
| GET/PUT/PATCH/DELETE | `/api/common/district/{id}/` | No | District detail/update/delete |
| GET/POST | `/api/common/address/` | Yes | User address list/create |
| GET/PUT/PATCH/DELETE | `/api/common/address/{id}/` | Yes | Address detail/update/delete |

District filter:

```text
?region=<region_id>
```

Address create body:

```json
{
  "region": "region-uuid",
  "district": "district-uuid",
  "address_line": "Bunyodkor street 1",
  "is_default": true
}
```

### News

| Method | Endpoint | Auth | Tavsif |
| --- | --- | --- | --- |
| GET | `/api/news/news/` | No | Oxirgi 5 ta news |
| GET | `/api/news/news/{id}/` | No | News detail |

News endpoint hozir read-only ishlaydi.

## Swagger

Swagger UI:

```text
http://127.0.0.1:8000/api/docs/
```

OpenAPI schema:

```text
http://127.0.0.1:8000/api/schema/
```

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

Serverni ishga tushirish:

```powershell
python manage.py runserver
```

## Muhim Eslatmalar

- Auth talab qiladigan endpointlarda `Authorization: Bearer <access_token>` kerak.
- `phone_number` formati `+998901234567` kabi bo'lishi kerak.
- OTP 6 xonali kod.
- OTP resend cooldown 30 soniya.
- OTP default amal qilish vaqti service bo'yicha 2 daqiqa.
- Duplicate phone: `bu raqam mavjut.`
- Duplicate gmail: `bu gmail mavjut.`
- Development uchun SQLite ishlaydi.
- Production uchun Docker Compose PostgreSQL ishlatadi.
