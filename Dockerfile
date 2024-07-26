FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app
COPY main.py /app

RUN pip install --no-cache-dir -r requirements.txt

ENV AUTH_TOKEN "<GOPRO_AUTH_TOKEN>"
ENV ACTION "download"
ENV START_PAGE  "1"
# Should mean all
ENV PAGES "1000000"
ENV PER_PAGE "15"
ENV DOWNLOAD_PATH "./download"
ENV PROGRESS_MODE "noline"
ENV RESOLUTION "source"
ENV S3_ENDPOINT_URL "s3.us-west-2.amazonaws.com"
ENV AWS_ACCESS_KEY_ID "<AWS_ACCESS_KEY_ID>"
ENV AWS_SECRET_ACCESS_KEY "<AWS_SECRET_ACCESS_KEY>"
ENV S3_BUCKET_NAME "<S3_BUCKET_NAME>"

CMD ["sh", "-c", "python3 main.py --action $ACTION --start-page $START_PAGE --pages $PAGES --per-page $PER_PAGE --download-path $DOWNLOAD_PATH --progress-mode $PROGRESS_MODE --resolution $RESOLUTION"]
