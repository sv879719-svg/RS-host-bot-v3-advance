# Hum Python ka official image use kar rahe hain
FROM python:3.10-slim

# System updates aur PHP install karne ke liye
RUN apt-get update && apt-get install -y \
    php-cli \
    php-sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Work directory set karein
WORKDIR /app

# Requirements copy aur install karein
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Baaki saari files copy karein
COPY . .

# Port expose karein (Render automatically isse detect kar leta hai)
EXPOSE 10000

# App start karne ki command
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "main:app"]