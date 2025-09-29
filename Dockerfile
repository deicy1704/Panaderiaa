FROM python:3.13-slim
# Establecer el directorio de trabajo
WORKDIR /app
# Copiar requirements.txt e instalar dependencias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copiar el resto del código
COPY . .
EXPOSE 5053

#CMD [ "python", "main.py" ]
CMD sh -c "gunicorn --bind 0.0.0.0:5000 --workers 4 --forwarded-allow-ips=*wsgi:app"
