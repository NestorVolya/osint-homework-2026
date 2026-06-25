FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    python -m spacy download uk_core_news_sm

COPY . .

RUN mkdir -p output

# API keys must be provided at runtime via --env-file; never bake into image
ENTRYPOINT ["python", "-m", "pipeline.run"]
