FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app
COPY main.py /app

RUN pip install --no-cache-dir -r requirements.txt

ENV AUTH_TOKEN "<GOPRO_AUTH_TOKEN>"
ENV ACTION "download"
ENV START_PAGE  "1"
ENV PAGES "1"
ENV PER_PAGE "30"
ENV DOWNLOAD_PATH "./download"
ENV PROGRESS_MODE "newline"

EXPOSE 80

CMD ["sh", "-c", "python3 main.py --action $ACTION --start-page $START_PAGE --pages $PAGES --per-page $PER_PAGE --download-path $DOWNLOAD_PATH --progress-mode $PROGRESS_MODE"]
