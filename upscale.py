import cv2
import glob
import os
from basicsr.archs.rrdbnet_arch import RRDBNet

from realesrgan import RealESRGANer
from realesrgan.archs.srvgg_arch import SRVGGNetCompact

from upload import uploader


def run(input='inputs',
        model_name='RealESRGAN_x4plus',
        output='results',
        outscale=4,
        suffix='',
        tile=0,
        tile_pad=10,
        pre_pad=0,
        face_enhance=False,
        fp32=False,
        alpha_upsampler='realesrgan',
        ext='auto',
        gpu_id=None,
        entity='files',
        upload_endpoint=None):
    """_summary_

    Args:
        input (str, optional): _description_. Defaults to 'inputs'.
        model_name (str, optional): _description_. Defaults to 'RealESRGAN_x4plus'.
        output (str, optional): _description_. Defaults to 'results'.
        outscale (int, optional): _description_. Defaults to 4.
        suffix (str, optional): _description_. Defaults to 'out'.
        tile (int, optional): _description_. Defaults to 0.
        tile_pad (int, optional): _description_. Defaults to 10.
        pre_pad (int, optional): _description_. Defaults to 0.
        face_enhance (bool, optional): _description_. Defaults to False.
        fp32 (bool, optional): _description_. Defaults to False.
        alpha_upsampler (str, optional): _description_. Defaults to 'realesrgan'.
        ext (str, optional): _description_. Defaults to 'auto'.
        gpu_id (_type_, optional): _description_. Defaults to None.
        upload_endpoint (_type_, optional): _description_. Defaults to None.

    Raises:
        ValueError: _description_
    """
    # determine models according to model names
    model_name = model_name.split('.')[0]
    if model_name in ['RealESRGAN_x4plus', 'RealESRNet_x4plus']:  # x4 RRDBNet model
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
        netscale = 4
    elif model_name in ['RealESRGAN_x4plus_anime_6B']:  # x4 RRDBNet model with 6 blocks
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=6, num_grow_ch=32, scale=4)
        netscale = 4
    elif model_name in ['RealESRGAN_x2plus']:  # x2 RRDBNet model
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=2)
        netscale = 2
    elif model_name in ['realesr-animevideov3']:  # x4 VGG-style model (XS size)
        model = SRVGGNetCompact(num_in_ch=3, num_out_ch=3, num_feat=64, num_conv=16, upscale=4, act_type='prelu')
        netscale = 4

    # determine model paths
    model_path = os.path.join('experiments/pretrained_models', model_name + '.pth')
    if not os.path.isfile(model_path):
        model_path = os.path.join('realesrgan/weights', model_name + '.pth')
    if not os.path.isfile(model_path):
        raise ValueError(f'Model {model_name} does not exist.')

    # restorer
    upsampler = RealESRGANer(
        scale=netscale,
        model_path=model_path,
        model=model,
        tile=tile,
        tile_pad=tile_pad,
        pre_pad=pre_pad,
        half=not fp32,
        gpu_id=gpu_id)

    if face_enhance:  # Use GFPGAN for face enhancement
        from gfpgan import GFPGANer
        face_enhancer = GFPGANer(
            model_path='https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth',
            upscale=outscale,
            arch='clean',
            channel_multiplier=2,
            bg_upsampler=upsampler)
    os.makedirs(output, exist_ok=True)

    if os.path.isfile(input):
        paths = [input]
    else:
        paths = sorted(glob.glob(os.path.join(input, '*')))

    for idx, path in enumerate(paths):
        imgname, extension = os.path.splitext(os.path.basename(path))
        print('Processing', idx, imgname)

        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if len(img.shape) == 3 and img.shape[2] == 4:
            img_mode = 'RGBA'
        else:
            img_mode = None

        try:
            if face_enhance:
                _, _, result = face_enhancer.enhance(img, has_aligned=False, only_center_face=False, paste_back=True)
            else:
                result, _ = upsampler.enhance(img, outscale=outscale)
        except RuntimeError as error:
            print('Error', error)
            print('If you encounter CUDA out of memory, try to set --tile with a smaller number.')
        else:
            if ext == 'auto':
                extension = extension[1:]
            else:
                extension = ext
            if img_mode == 'RGBA':  # RGBA images should be saved in png format
                extension = 'png'
            if suffix == '':
                save_path = os.path.join(output, f'{imgname}.{extension}')
            else:
                save_path = os.path.join(output, f'{imgname}_{suffix}.{extension}')
            cv2.imwrite(save_path, result)
            print('writing to disk')
            # Execute an upload here
            if upload_endpoint:
                uploader.upload(save_path, upload_endpoint, entity=entity)

