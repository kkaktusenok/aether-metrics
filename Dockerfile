FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1
ENV MONITOR_INTERVAL=1

ENV DISCORD_TOKEN=""

WORKDIR /app

COPY src/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

CMD [ "python", "monitor.py" ]