FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app/agente

COPY agente/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agente/ .
# O guia de triagem fica fora da pasta do agente (fonte única no repositório).
COPY 02-verticais/advocacia/previdenciario/triagem-por-beneficio.md /app/02-verticais/advocacia/previdenciario/triagem-por-beneficio.md

# Banco e documentos ficam em /app/agente/dados: monte um volume persistente aqui.
RUN useradd --create-home agente && mkdir -p dados && chown -R agente dados
USER agente

EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]
