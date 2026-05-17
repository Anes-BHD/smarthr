# ── Stage 1: dependency builder ──────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Only copy the requirements file first to leverage layer caching
COPY agentsmarthr/requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: runtime image ────────────────────────────────────────────────────
FROM python:3.12-slim

# Non-root user for security
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1001 agent

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy chatbot source code
COPY agentsmarthr/ .

# Ensure the user owns the workdir
RUN chown -R agent:agent /app

USER agent

EXPOSE 8080

# Uvicorn binds on 0.0.0.0:8080; workers can be tuned via env var
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
