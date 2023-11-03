import os
import sys
import json
import argparse

import signal
import readchar

import requests

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

    def get_ids_from_media(self, media):
        return [x["id"] for x in media]

    def get_filenames_from_media(self, media):
        return [x["filename"] for x in media]

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
                "fields": "id,created_at,content_title,filename,file_extension",
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


    def download_media_ids(self, ids, filepath, progress_mode="inline"):
        download_url = "{}/media/x/zip/source".format(self.host)
        params = {
            "ids": ",".join(ids),
            "access_token": self.auth_token,
        }

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        }

        resp = requests.get(download_url, params=params, headers=headers, stream=True)
        if resp.status_code != 200:
            print("request failed with status code: {} and error: {}".format(resp.status_code, self.parse_error(resp)))
            return False

        downloaded_size = 0
        print('downloading to {}'.format(filepath))
        with open(filepath, 'wb') as file:
            # Iterate over the response in chunks 8K chunks
            for chunk in resp.iter_content(chunk_size=8192):
                # Write the chunk to the file
                file.write(chunk)

                # Update the downloaded size
                downloaded_size += len(chunk)
                progress = ((downloaded_size / 1024) / 1024)

                if progress_mode == "inline":
                    # Print the progress
                    print(f"\rdownloaded: {progress:.2f}MB ({downloaded_size}) bytes", end='')

                if progress_mode == "newline":
                    print(f"downloaded: {progress:.2f}MB ({downloaded_size}) bytes")

        print("\ndownload completed!")


def main():
    actions = ["list", "download"]
    progress_modes = ["inline", "newline", "noline"]

    parser = argparse.ArgumentParser(prog="gopro")
    parser.add_argument("--action", help="action to execute. supported actions: {}".format(",".join(actions)), default="download")
    parser.add_argument("--pages", nargs="?", help="number of pages to iterate over", type=int, default=sys.maxsize)
    parser.add_argument("--per-page", nargs="?", help="number of items per page", type=int, default=30)
    parser.add_argument("--start-page", nargs="?", help="starting page", type=int, default=1)
    parser.add_argument("--download-path", help="path to store the download zip", default="./download")
    parser.add_argument("--progress-mode", help="showing download progress. supported modes: {}".format(",".join(progress_modes)), default=progress_modes[0])

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
        filenames = gpp.get_filenames_from_media(media)
        print("listing page({}) media({})".format(page, filenames))

        if args.action == "download":
            filepath = "{}/{}_page.zip".format(args.download_path, page)
            ids = gpp.get_ids_from_media(media)
            gpp.download_media_ids(ids, filepath, progress_mode=args.progress_mode)


if __name__ == "__main__":
    main()
