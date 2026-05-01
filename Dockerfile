# Python muhitini o'rnatish
FROM python:3.12-slim

# Docker ichidagi ishchi papka
WORKDIR /app

# Kutubxonalarni o'rnatish uchun fayllarni nusxalash
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Loyiha fayllarini to'liq nusxalash
COPY . .

# Django ishga tushadigan port
EXPOSE 8000

# Loyihani ishga tushirish buyrug'i
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
