FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# playwright install-deps installs all required system libraries automatically
RUN playwright install-deps chromium
RUN playwright install chromium

RUN mkdir -p data/raw data/normalized

COPY src/ ./src/

ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

CMD ["python", "src/worker_html.py"]
