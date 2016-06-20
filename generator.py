import os
import templates as tl
from b64ext import *
import random
import string


IMAGES = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}


def randomboundary(length=40):
    alphabet = string.digits + string.ascii_letters + "'()+_,-./:=?"
    return ''.join(random.choice(alphabet) for i in range(length)) + ':-:'


def generate_boundary(text):
    boundary = randomboundary()
    while '--' + boundary in text:
        boundary = randomboundary()
    return boundary


def gen_parts(dir_, boundary, images=IMAGES, **kwargs):
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


def gen_message(dir_, **kwargs):
    user_input = ''.join(filter(lambda x: isinstance(x, str), kwargs.values()))

    boundary = generate_boundary(tl.PART + tl.MESSAGE + user_input)

    kwargs['fromname'] = encode_name(kwargs['fromname'])
    kwargs['toname'] = encode_name(kwargs['toname'])

    parts = gen_parts(dir_, boundary, **kwargs)
    params = {
        'parts': parts,
        'boundary': boundary
    }
    params.update(kwargs)

    return tl.MESSAGE % params
