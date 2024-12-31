#!/bin/bash

# Create the download directory if it doesn't exist
# NOTE: This is the path within the docker container
# For host destination use:
#
# docker run -v /path/to/downloads:/app/download
if [ ! -d "${DOWNLOAD_PATH}" ]; then
  echo "Creating download directory: ${DOWNLOAD_PATH}"
  mkdir -p "${DOWNLOAD_PATH}"
fi

# Start the main application
exec python3 main.py --action "${ACTION}" --start-page "${START_PAGE}" --pages "${PAGES}" --per-page "${PER_PAGE}" --download-path "${DOWNLOAD_PATH}" --progress-mode "${PROGRESS_MODE}"
