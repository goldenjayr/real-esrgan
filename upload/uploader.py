from upload import config
from upload.client import Client


def upload(file_path, url=config.UPLOAD_API_URL, entity='files'):
    client = Client(url, config.MAX_UPLOAD_BYTE_LENGHT)
    print(f'Uploading file: {file_path} to {url}')
    client.upload_file(file_path, entity=entity)
