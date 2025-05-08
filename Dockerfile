FROM python:3.12.10-bookworm

RUN apt update && \
    apt install -y --no-install-recommends \
    jq && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN python3 -m pip install --no-cache-dir --progress-bar off -U pip && \
    python3 -m pip install --no-cache-dir --progress-bar off torch --index-url https://download.pytorch.org/whl/cpu && \
    python3 -m pip install --no-cache-dir --progress-bar off -e .

CMD ["sleep", "infinity"]
