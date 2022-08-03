import os

HOST = 'localhost'
PORT = 8080

APP_DIR = os.getcwd()
MEDIA_ROOT = os.path.join(APP_DIR, 'media')
MAX_UPLOAD_BYTE_LENGHT = 480 * 480  # 1M

API_URL = 'http://{}:{}'.format(HOST, PORT)
API_URL = 'https://dev-files.23point5.com/file/upload/entity'