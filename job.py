import requests
from requests.auth import HTTPBasicAuth
from upload import config
import upscale
import os


def scan_product_for_upscale():
    #  get all products with upscaed false
    resp = requests.get(
        config.API_URL + '/product?is_upscaled=false&fields=id,product_name,status,is_upscaled,wrap_modes&limit=1',
        auth=HTTPBasicAuth(config.USERNAME, config.PASSWORD))
    # resp = requests.get(
    #     config.API_URL +
    #     '/product?id=586b9ec9-bdaa-4eb2-aeb6-bc31f85f04e9&fields=id,product_name,status,is_upscaled,wrap_modes&limit=1',
    #     auth=HTTPBasicAuth(config.USERNAME, config.PASSWORD))

    data = resp.json()

    # get all the raw files and reduce it into an array
    for product in data:
        print('product')
        product_id = product['id']
        product_name = product['product_name']
        print(f'Now Processing PRODUCT ID: {product_id} -- PRODUCT NAME: {product_name}')
        model_components = product['wrap_modes'][0]['modelComponents']

        images = []
        for component in model_components:
            for element in component['elements']:
                if element and 'type' in element and element["type"] == 'image':
                    # check raw if it is not a stock photo
                    if '/stock-image/' in element['raw']:
                        pass
                    else:
                        #  add raw image to images list
                        images.append(element['raw'])

        # get unique list
        unique_images = list(set(images))
        print('Unique Images', unique_images)

        # get all images and store it in inputs folder
        input_directory = 'inputs'
        for image in unique_images:
            img_data = requests.get(f'{config.UPLOAD_API_URL}/file?path={image}').content
            _, entity, file_name = image.split('/')
            input_file_path = f'{input_directory}/{file_name}'
            if not os.path.exists(input_directory):
                os.mkdir(input_directory)
            with open(input_file_path, 'wb') as file:
                file.write(img_data)

        # execute upscaler for all images in inputs folder
        upscale.run(upload_endpoint=config.UPLOAD_API_URL, tile=64, fp32=True, entity=entity)

        # delete all the files in inputs folder after it is done processing
        print('Removing files in input directory.')
        for file in os.listdir(input_directory):
            print(f'Removing {file}')
            os.remove(os.path.join(input_directory, file))
            print(f"File {file} has been removed successfully.")

        # delete all the files in results folder after it is done processing
        print('Removing files in output directory.')
        output_directory = 'results'
        for file in os.listdir(output_directory):
            print(f'Removing {file}')
            os.remove(os.path.join(output_directory, file))
            print(f"File {file} has been removed successfully.")

        # update product upscale status
        print(f'Updating Product {product_name} -- is_upscaled: true')
        payload = {'id': product_id, 'is_upscaled': True, 'metadata': {"initiated_by": 'upscaler'}}
        res = requests.put(
            config.API_URL + '/product', auth=HTTPBasicAuth(config.USERNAME, config.PASSWORD), data=payload)
        if res.ok:
            print(f'Product ID: {product_id} -- {product_name}  Done')