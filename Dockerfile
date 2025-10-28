# Dockerfile para desplegar el Agente Personal
FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    calcurse \
    libnotify-bin \
    pulseaudio-utils \
    mpv \
    && rm -rf /var/lib/apt/lists/*

# Configurar directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY pyproject.toml uv.lock ./

# Instalar UV y dependencias
RUN pip install uv && \
    uv sync --frozen

# Copiar código fuente
COPY . .

# Crear directorios necesarios
RUN mkdir -p data/logs data/db data/cache

# Variables de entorno por defecto
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Comando de inicio
CMD ["uv", "run", "python", "main.py"]
