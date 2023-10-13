import os
import requests
import sys

sys.stdout = open(1, "w", encoding="utf-8", closefd=False)

class GoProPlus:
    def __init__(self, auth_token):
        self.host = "https://api.gopro.com"
        self.auth_token = auth_token

    def get_ids_from_media(self, media):
        return [x["id"] for x in media]

    def get_media(self):
        media_url = "{}/media/search".format(self.host)
        params = {
#             "fields": "captured_at,content_title,content_type,created_at,gopro_user_id,file_size,id,token,type,resolution,filename,file_extension"
        }
        headers = {
            "Accept-Charset": "utf-8",
            "Accept": "application/vnd.gopro.jk.media+json; version=2.0.0",
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.auth_token),
        }

        resp = requests.get(media_url, params=params, headers=headers)
        content = resp.json()
        media = content["_embedded"]["media"]
        return media

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

        downloaded_size = 0
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
    if "AUTH_TOKEN" not in os.environ:
        print("invalid AUTH_TOKEN env variable set")
        return

    auth_token = os.environ["AUTH_TOKEN"]
    gpp = GoProPlus(auth_token)

    media = gpp.get_media()
    ids = gpp.get_ids_from_media(media)

    filename = './download.zip'
    gpp.download_media_ids(ids, filename)



if __name__ == "__main__":
    main()
