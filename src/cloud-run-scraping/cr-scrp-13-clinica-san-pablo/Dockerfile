FROM python:3.11.2-slim

WORKDIR /app

# Copiar requirements primero y luego instalar
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY src/ .

# Instalar dependencias del sistema necesarias para OCR y scraping
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgl1-mesa-dev \
        libglib2.0-0 \
        libicu-dev \
        wget python3-h5py \
        python3-opencv \
    && rm -rf /var/lib/apt/lists/*

# Elimina lo que ya no se necesita en runtime
RUN apt-get remove -y libgl1-mesa-dev && apt-get autoremove -y

ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PORT=8080

# Iniciar con gunicorn
CMD exec gunicorn --bind 0.0.0.0:8080 --workers 1 --threads 8 --timeout 0 main:app
