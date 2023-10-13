import urllib.request
import re
import json
import sys
import requests
import os


class GoProPlus:
    def __init__(self, bearer):
        self.GOPRO_API_ENDPOINT = "https://api.gopro.com"
        self.GOPRO_API_GET_MEDIA = "https://api.gopro.com/media/search"
        self.GOPRO_API_BEARER = bearer

    def getMediaList(self):
        headers = {
            'Accept-Charset': 'utf-8',
            'Accept': 'application/vnd.gopro.jk.media+json; version=2.0.0',
            'Content-Type': 'application/json',
            'Authorization': self.GOPRO_API_BEARER,
        }

        url = self.GOPRO_API_GET_MEDIA + "?fields=captured_at,content_title,content_type,created_at,gopro_user_id,file_size,id,token,type,resolution,filename,file_extension"

        request = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(request)

        content = resp.read()
        out = str(content, encoding="utf-8")

        print(out)

def main():
    if "AUTH_TOKEN" not in os.environ:
        print('invalid AUTH_TOKEN env variable set')
        return

    token = os.environ['AUTH_TOKEN']
    gpp = GoProPlus(token)
    gpp.getMediaList()


if __name__ == '__main__':
    main()
