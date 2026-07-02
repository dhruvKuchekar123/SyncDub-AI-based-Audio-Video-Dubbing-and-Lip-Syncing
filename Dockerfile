# SyncDub backend — CPU baseline image (Stage 0 portability; Founder OS Ch. 8).
# Voice cloning (XTTS sidecar env) is not included; the pipeline falls back to
# Edge-TTS voices inside the container. Wav2Lip weights (~436MB) download on
# first job via lipdub/wav2lip_wrapper.py; mount /app/backend/Wav2Lip_repo/checkpoints
# as a volume to persist them across container rebuilds.
FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ backend/

WORKDIR /app/backend
EXPOSE 8000
CMD ["python", "server.py"]
