import os
import sys
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
        # for each id we need to make a request to get the download url
        resultados = []

        for id in ids:
            url = "{}/media/{}/download".format(self.host, id)
            params = {
                "access_token": self.auth_token,
            }

            headers = {
                "accept": "application/json, charset=utf-8",
                "Authorization": "Bearer {}".format(self.auth_token),
            }

            resp = requests.get(url, params=params, headers=headers).json()
            url_do_arquivo = resp['_embedded']['files'][0]['url']
            nome_do_arquivo = url_do_arquivo.split('/')[-1]
            nome_do_arquivo = resp['filename']

            caminho_do_arquivo = os.path.join(filepath, nome_do_arquivo)

            # Tentar fazer o download do arquivo usando streaming
            try:
                # Criar um objeto de resposta com streaming ativado
                r = requests.get(url_do_arquivo, stream=True)

                # Verificar se o código de status da resposta é 200 (OK)
                if r.status_code == 200:
                    # Abrir o arquivo em modo de escrita binária
                    with open(caminho_do_arquivo, 'wb') as f:
                        # Definir o tamanho do pedaço (chunk) em bytes
                        tamanho_do_pedaco = 1024 * 1024

                        # Obter o tamanho total do arquivo em bytes a partir do cabeçalho da resposta
                        tamanho_total = int(r.headers.get('content-length', 0))

                        # Inicializar uma variável para armazenar o tamanho baixado em bytes
                        tamanho_baixado = 0

                        # Percorrer os pedaços da resposta
                        for pedaco in r.iter_content(tamanho_do_pedaco):
                            # Escrever o pedaço no arquivo
                            f.write(pedaco)

                            # Incrementar o tamanho baixado com o tamanho do pedaço
                            tamanho_baixado += len(pedaco)

                            # Calcular a porcentagem de progresso
                            porcentagem = int(tamanho_baixado * 100 / tamanho_total)

                            # Mostrar na tela o progresso do download
                            print(f'Baixando {nome_do_arquivo}: {porcentagem}%')

                    # Fechar o objeto de resposta
                    r.close()

                    # Mostrar na tela que o download foi concluído com sucesso
                    print(f'{nome_do_arquivo} baixado com sucesso!')

                    # Adicionar um resultado com status de sucesso na lista de resultados
                    resultados.append({'id': id, 'status': 'sucesso', 'arquivo': caminho_do_arquivo})

                    # upload to s3
                    print(f'Uploading: {caminho_do_arquivo} to {os.environ["S3_BUCKET_NAME"]}')
                    S3_ENDPOINT_URL = "https://" + os.environ["S3_ENDPOINT_URL"]
                    b2session = boto3.session.Session(aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"], aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])
                    b2 = b2session.resource(service_name='s3', endpoint_url=S3_ENDPOINT_URL)
                    # bucket = b2.Bucket(os.environ["S3_BUCKET_NAME"])
                    # obj = bucket.put_object(Body=open(caminho_do_arquivo, mode='rb'),
                    #                         Key=os.path.basename(caminho_do_arquivo))
                    b2.Object(os.environ["S3_BUCKET_NAME"], nome_do_arquivo).upload_file(caminho_do_arquivo,
                            ExtraArgs={'ContentType': 'text/pdf'},
                            Config=transfer_config,
                            Callback=ProgressPercentage(caminho_do_arquivo)
                            )
                    # Create a response dict with the values returned from B2
                    # response = {attr: getattr(obj, attr) for attr in ['e_tag', 'version_id']}
                    # print(f'Success! Response is: {response}')
                    
                    # Delete local file
                    print(f'Deleting local file: {caminho_do_arquivo}')
                    os.remove(caminho_do_arquivo)

                else:
                    # Mostrar na tela que o download falhou por causa do código de status
                    print(f'{nome_do_arquivo} não pôde ser baixado: código de status {r.status_code}')

                    # Adicionar um resultado com status de erro na lista de resultados
                    resultados.append({'id': id, 'status': 'erro', 'motivo': f'código de status {r.status_code}'})

            except Exception as e:
                # Mostrar na tela que o download falhou por causa de uma exceção
                print(f'{nome_do_arquivo} não pôde ser baixado: {e}')

                # Adicionar um resultado com status de erro na lista de resultados
                resultados.append({'id': id, 'status': 'erro', 'motivo': str(e)})


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
            filepath = "{}".format(args.download_path)
            ids = gpp.get_ids_from_media(media)
            gpp.download_media_ids(ids, filepath, progress_mode=args.progress_mode)


if __name__ == "__main__":
    main()
