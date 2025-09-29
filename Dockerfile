# Copiar requirements.txt primero
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Luego copiar el resto del código
COPY . .

# Exponer puerto y comando final
EXPOSE 5053
CMD ["gunicorn", "--bind", "0.0.0.0:5053", "app1:app"]
