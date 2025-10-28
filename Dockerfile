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

# Copiar archivos de requirements primero (para cache de Docker)
COPY pyproject.toml ./

# Instalar dependencias Python directamente
RUN pip install --no-cache-dir \
    openai>=1.54.0 \
    httpx>=0.27.0 \
    rich>=13.7.0 \
    typer>=0.12.0 \
    pydantic>=2.9.0 \
    pydantic-settings>=2.5.0 \
    python-dotenv>=1.0.0 \
    apscheduler>=3.10.0 \
    watchdog>=4.0.0 \
    python-telegram-bot>=21.0 \
    fastapi>=0.115.0 \
    uvicorn>=0.30.0 \
    websockets>=13.0 \
    icalendar>=6.0.0 \
    caldav>=1.3.0 \
    redis>=5.0.0 \
    sqlalchemy>=2.0.0 \
    aiosqlite>=0.20.0 \
    pyyaml>=6.0.3 \
    psycopg2-binary>=2.9.11 \
    asyncpg>=0.30.0

# Copiar código fuente
COPY . .

# Crear directorios necesarios
RUN mkdir -p data/logs data/db data/cache

# Variables de entorno por defecto
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV LOG_LEVEL=INFO

# Comando de inicio
CMD ["python", "main.py"]
