import os
import sys
import time
from dateutil.parser import parse
import json
import argparse

import signal
import readchar
import threading

import requests
import boto3.session

from boto3.s3.transfer import TransferConfig

transfer_config = TransferConfig(multipart_threshold=1024 * 25,
                                 max_concurrency=10,
                                 multipart_chunksize=1024 * 25,
                                 use_threads=True)

sys.stdout = open(1, "w", encoding="utf-8", closefd=False)


def handler(signum, frame):
    print("\ninterrupting the process. do you really want to exit? (y/n) ")

    res = readchar.readchar()
    if res == 'y':
        print("stopping the process!")
        exit(1)
    else:
        print("continue executing...")


signal.signal(signal.SIGINT, handler)


class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()


class GoProPlus:
    def __init__(self, auth_token):
        self.base = "api.gopro.com"
        self.host = "https://{}".format(self.base)
        self.auth_token = auth_token

    def validate(self):
        headers = {
            "Authorization": "Bearer {}".format(self.auth_token),
        }

        resp = requests.get("{}/search/media/labels/top?count=1".format(self.host), headers=headers)
        if resp.status_code != 200:
            print("failed to validate auth token. issue a new one")
            return False

        return True

    def parse_error(self, resp):
        try:
            err = resp.json()
        except:
            err = resp.text
        return err
    
    def get_media_data(self, media):
        return [{"filename": x["filename"], "file_extension": x["file_extension"], "id": x["id"], "captured_at": x["captured_at"]} for x in media]
    
    def get_media(self, start_page=1, pages=sys.maxsize, per_page=30):
        media_url = "{}/media/search".format(self.host)

        headers = {
            "Authority": self.base,
            "Accept-Charset": "utf-8",
            "Accept": "application/vnd.gopro.jk.media+json; version=2.0.0",
            "Origin": self.host,
            "Referer": "{}/".format(self.host),
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.auth_token),
        }

        output_media = {}
        total_pages = 0
        current_page = start_page
        while True:
            params = {
                # for all fields check some requests on GoProPlus website requests
                "fields": "id,captured_at,content_title,filename,file_extension",
                "per_page": per_page,
                "page": current_page,
                "type": "",
            }

            resp = requests.get(media_url, params=params, headers=headers)
            if resp.status_code != 200:
                err = self.parse_error(resp)
                print("failed to get media for page {}: {}. try renewing the auth token".format(current_page, err))
                return []

            content = resp.json()
            output_media[current_page] = content["_embedded"]["media"]
            print("page parsed ({}/{})".format(current_page, total_pages))

            if total_pages == 0:
                total_pages = content["_pages"]["total_pages"]

            if current_page >= total_pages or current_page >= (start_page + pages) - 1:
                break

            current_page += 1

        return output_media

    def download_media_ids(self, ids_with_dates, filepath, action="download", progress_mode="inline", resolution="source"):
        # for each id we need to make a request to get the download url
        results = []

        for item in ids_with_dates:
            url = "{}/media/{}/download".format(self.host, item['id'])
            params = {
                "access_token": self.auth_token,
            }

            headers = {
                "accept": "application/json, charset=utf-8",
                "Authorization": "Bearer {}".format(self.auth_token),
            }

            resp = requests.get(url, params=params, headers=headers).json()

            file_url = None
            if resolution == "1080p":
                file_url = resp['_embedded']['files'][0]['url']
            if resolution == "source":
                # Extract the URL for the label=source item under variations
                for variation in resp['_embedded']['variations']:
                    if variation['label'] == 'source':
                        file_url = variation['url']
                        break
                    else:
                        file_url = resp['_embedded']['files'][0]['url']
            else:
                print(f'Invalid resolution. {resolution} not found')

            file_name = resp['filename']
            # if filename is '' then use the item['id'] as filename
            if file_name == '':
                file_name = item['id'] + '.' + item['file_extension']
            file_path = os.path.join(filepath, file_name)

            # See if file exists:
            if os.path.exists(file_path):
                print(f'{file_name} already exists. skipping...')
                results.append({'id': id, 'status': 'skipped', 'file': file_path})
                continue
            else:
              # Try to download the file using streaming
              try:
                  # Create a response object with streaming enabled
                  r = requests.get(file_url, stream=True)

                  # Check if the response status code is 200 (OK)
                  if r.status_code == 200:
                      # Open the file in binary write mode
                      with open(file_path, 'wb') as f:
                          # Define the chunk size in bytes
                          piece_size = 1024 * 1024

                          # Get the total file size in bytes from the response header
                          total_size = int(r.headers.get('content-length', 0))

                          # Initialize a variable to store the downloaded size in bytes
                          downloaded_size = 0

                          # Traverse the chunks of the response
                          for chunk in r.iter_content(piece_size):
                              # Write the chunk to the file
                              f.write(chunk)

                              # Increase the downloaded size by the size of the chunk
                              downloaded_size += len(chunk)

                              # Calculate the progress percentage
                              percentage = int(downloaded_size * 100 / total_size)

                              if progress_mode == "inline":
                                # Display the download progress on the screen
                                print(f'\rDownloading {file_name}: {percentage}%', end='')

                              if progress_mode == "newline":
                                # Display the download progress on the screen
                                print(f'Downloading {file_name}: {percentage}%')

                      # Close the response object
                      r.close()

                      # Display on the screen that the download was successfully completed
                      print(f'\n{file_name} download successful!')

                      # Set the captured_date of the file with item['captured_at']
                      captured_date = item['captured_at']

                      # Parse the date string to a datetime object
                      captured_date = parse(captured_date)

                      # Convert the datetime object to a timestamp
                      timestamp = captured_date.timestamp()

                      # Set the access time and the modification time
                      os.utime(file_path, (timestamp, timestamp))

                      # Add a result with a success status to the results list
                      results.append({'id': item['id'], 'status': 'sucesso', 'file': file_path})

                      # upload to s3
                      if action == 'download-upload':
                        print(f'Uploading: {file_path} to {os.environ["S3_BUCKET_NAME"]}')
                        S3_ENDPOINT_URL = "https://" + os.environ["S3_ENDPOINT_URL"]
                        b2session = boto3.session.Session(aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"], aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])
                        b2 = b2session.resource(service_name='s3', endpoint_url=S3_ENDPOINT_URL)

                        b2.Object(os.environ["S3_BUCKET_NAME"], file_name).upload_file(file_path,
                                ExtraArgs={'ContentType': 'text/pdf'},
                                Config=transfer_config,
                                Callback=ProgressPercentage(file_path)
                                )

                        # Delete local file
                        print(f"\n")
                        print(f'Deleting local file: {file_path}')
                        os.remove(file_path)

                  else:
                      # Display on the screen that the download failed due to the status code
                      print(f'{file_name} could not be downloaded: status code {r.status_code}')

                      # Add a result with an error status to the results list
                      results.append({'id': id, 'status': 'erro', 'reason': f'código de status {r.status_code}'})

              except Exception as e:
                  # Display on the screen that the download failed due to an exception
                  print(f'{file_name} could not be downloaded: {e}')

                  # Add a result with an error status to the results list
                  results.append({'id': item['id'], 'status': 'erro', 'reason': str(e)})


def main():
    actions = ["list", "download"]
    progress_modes = ["inline", "newline", "noline"]
    resolutions = ["1080p", "source"]

    parser = argparse.ArgumentParser(prog="gopro")
    parser.add_argument("--action", help="action to execute. supported actions: {}".format(",".join(actions)),
                        default="download")
    parser.add_argument("--pages", nargs="?", help="number of pages to iterate over", type=int, default=sys.maxsize)
    parser.add_argument("--per-page", nargs="?", help="number of items per page", type=int, default=30)
    parser.add_argument("--start-page", nargs="?", help="starting page", type=int, default=1)
    parser.add_argument("--download-path", help="path to store the download zip", default="./download")
    parser.add_argument("--progress-mode",
                        help="showing download progress. supported modes: {}".format(",".join(progress_modes)),
                        default=progress_modes[0])
    parser.add_argument("--resolution", help="resolution to download, use: {}".format(",".join(resolutions)),
                        default=resolutions[1])

    args = parser.parse_args()

    if "AUTH_TOKEN" not in os.environ:
        print("invalid AUTH_TOKEN env variable set")
        return

    auth_token = os.environ["AUTH_TOKEN"]
    gpp = GoProPlus(auth_token)
    if not gpp.validate():
        return -1

    media_pages = gpp.get_media(start_page=args.start_page, pages=args.pages, per_page=args.per_page)
    if not media_pages:
        print('failed to get media')
        return -1

    for page, media in media_pages.items():
        mediadata = gpp.get_media_data(media)
        for filewithdate in mediadata:
          print("listing page({}) filename({}) date({})".format(page, filewithdate["filename"], filewithdate["captured_at"]))


        if args.action.startswith("download"):
            filepath = "{}".format(args.download_path)
            gpp.download_media_ids(mediadata, filepath, args.action, progress_mode=args.progress_mode,
                                   resolution=args.resolution)


if __name__ == "__main__":
    main()
