import os

HOST = 'localhost'
PORT = 8080

APP_DIR = os.getcwd()
MEDIA_ROOT = os.path.join(APP_DIR, 'media')
MAX_UPLOAD_BYTE_LENGHT = 480 * 480  # 1M

UPLOAD_API_URL = 'https://dev-files.23point5.com'
API_URL = 'https://dev-api.23point5.com'
USERNAME = '23point5'
PASSWORD = 'F0nch3rt0'