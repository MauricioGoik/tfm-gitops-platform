# Usamos una imagen base específica con versión fija (nunca :latest)
# python:3.13-slim es ARM64 nativo, perfecto para M4 y para AWS Graviton
FROM python:3.13-slim

# Buena práctica: no correr como root
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copiamos requirements primero para aprovechar el cache de Docker
# Si no cambia requirements.txt, Docker no reinstala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Cambiamos al usuario no-root
USER appuser

EXPOSE 8080

# Usamos la forma exec (array) en lugar de shell, más seguro
CMD ["python", "app.py"]
