import os
import math
import time
import uuid

import requests


class Client:

    def __init__(self, api_url, max_byte_length):
        self.api_url = api_url
        self.max_byte_length = max_byte_length

    def upload_file(self, file_path, entity='files'):
        file_size = os.path.getsize(file_path)
        filename = os.path.basename(file_path)
        headers = {"Filename": filename}

        body = {
            'filename': filename,
            'entity': entity,
            'total_file_size': str(file_size),
            'uuid': filename.split('.')[0]
        }

        with open(file_path, 'rb') as file:
            start = 0

            # In python2 12/5 equals to 2 if file_size int. So we are casting to float for compatibility
            chunk_count = math.ceil(float(file_size) / self.max_byte_length)
            print("Total chunk count:", chunk_count)
            body['total_parts'] = str(chunk_count)
            retry_timeout = 1
            sent_chunk_count = 0

            while True:
                end = min(file_size, start + self.max_byte_length)
                headers['Range'] = "bytes={}-{}/{}".format(start, end, file_size)

                file.seek(start)
                data = file.read(self.max_byte_length)
                body['part_index'] = str(sent_chunk_count)
                body['file'] = str({'filename': filename})

                start = end
                files = {'file': data}

                try:
                    response = requests.post(self.api_url + '/file/upload/entity', headers=headers, data=body, files=files)
                    print('RESPONSEEEEE -----', response.content)
                    if response.ok:
                        print('{}. chunk sent to server'.format(sent_chunk_count + 1))
                        sent_chunk_count += 1
                except requests.exceptions.RequestException as err:
                    print('Error while sending chunk to server. Retrying in {} seconds'.format(retry_timeout))
                    print('ERRRROOOOORRRR', err)
                    time.sleep(retry_timeout)

                    # Sleep for max 10 seconds
                    if retry_timeout < 10:
                        retry_timeout += 1
                    continue

                if sent_chunk_count >= chunk_count:
                    return True

            return False
