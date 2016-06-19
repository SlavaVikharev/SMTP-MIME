import os
import templates as tl
from b64ext import *


IMAGES = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}

BOUNDARY = '---thisIsABoundary:?:'

def gen_parts(dir_, boundary=BOUNDARY, images=IMAGES, **kwargs):
    parts = []

    for file in os.listdir(dir_):
        ext = os.path.splitext(file)[1].lower().lstrip('.')
        if ext not in images:
            continue

        encoded = ''
        with open(os.path.join(dir_, file), 'rb') as f:
            encoded = b64encode_bytes(f.read())

        params = {
            'file_ext': ext,
            'filename': file,
            'body_part': encoded,
            'boundary': boundary
        }
        params.update(kwargs)

        part = tl.PART % params
        parts.append(part)

    return '\n'.join(parts)


def gen_message(dir_, boundary=BOUNDARY, **kwargs):
    kwargs['from_name'] = encode_name(kwargs.get('from_name', 'From'))
    kwargs['to_name'] = encode_name(kwargs.get('to_name', 'To'))

    parts = gen_parts(dir_, boundary, **kwargs)
    params = {
        'parts': parts,
        'boundary': boundary
    }
    params.update(kwargs)
    return tl.MESSAGE % params
