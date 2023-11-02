import os
import sys
import json
import argparse

import requests

sys.stdout = open(1, "w", encoding="utf-8", closefd=False)


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
        return errk

    def get_ids_from_media(self, media):
        return [x["id"] for x in media]

    def get_media(self, pages=sys.maxsize, per_page=30):
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

        output_media = []
        total_pages = 0
        current_page = 1
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
                return False

            content = resp.json()
            output_media += content["_embedded"]["media"]

            if total_pages == 0:
                total_pages = content["_pages"]["total_pages"]

            if current_page > pages or current_page > total_pages:
                break

            print("page parsed ({}/{})".format(current_page, total_pages))
            current_page += 1

        return output_media


    def download_media_ids(self, ids, filename):
        print("attempting to download {}".format(",".join(ids)))

        download_url = "{}/media/x/zip/source".format(self.host)
        params = {
            "ids": ",".join(ids),
            "access_token": self.auth_token,
        }

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        }

        print("making request to {}".format(download_url, params, headers))
        resp = requests.get(download_url, params=params, headers=headers, stream=True)
        print("request completed")

        if resp.status_code != 200:
            print("request failed with status code: {} and error: {}".format(resp.status_code, self.parse_error(resp)))
            return False

        downloaded_size = 0
        print('downloading...')
        with open(filename, 'wb') as file:
            # Iterate over the response in chunks 8K chunks
            for chunk in resp.iter_content(chunk_size=8192):
                # Write the chunk to the file
                file.write(chunk)

                # Update the downloaded size
                downloaded_size += len(chunk)
                progress = ((downloaded_size / 1024) / 1024)

                # Print the progress
                print(f"\rdownloaded: {progress:.2f}MB ({downloaded_size}) bytes", end='')

        print("\ndownload completed!")


def main():
    actions = ["list", "download"]
    parser = argparse.ArgumentParser(prog='gopro')
    parser.add_argument('--action', help="support actions: {}".format(",".join(actions)))
    parser.add_argument('--pages', nargs='?', help='number of pages to iterate over', type=int)

    args = parser.parse_args()

    if "AUTH_TOKEN" not in os.environ:
        print("invalid AUTH_TOKEN env variable set")
        return

    auth_token = os.environ["AUTH_TOKEN"]
    gpp = GoProPlus(auth_token)
    if not gpp.validate():
        return -1

    pages = args.pages
    if pages == None or pages == 0:
        pages = sys.maxsize

    media = gpp.get_media(pages=pages)
    ids = gpp.get_ids_from_media(media)
    print(ids)

    if args.action == "download":
        filename = './download.zip'
        gpp.download_media_ids(ids, filename)



if __name__ == "__main__":
    main()
