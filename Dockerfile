FROM python:3.10-slim

WORKDIR /app

# Copy application files
COPY requirements.txt /app
COPY main.py /app

RUN pip install --no-cache-dir -r requirements.txt

# Default environment variables
ENV AUTH_TOKEN="<GOPRO_AUTH_TOKEN>"
ENV USER_ID="<GOPRO_USER_ID>"
ENV ACTION="download"
ENV START_PAGE="1"
# Should mean all
ENV PAGES="1000000"
ENV PER_PAGE="15"
# NOTE: This is the path within the docker container
# For host destination use:
#
# docker run -v /path/to/downloads:/app/download
ENV DOWNLOAD_PATH="./download"
ENV PROGRESS_MODE="noline"

# Add entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Use the entrypoint script to handle the creation of directories
ENTRYPOINT ["/app/entrypoint.sh"]
