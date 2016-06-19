import base64


def b64encode_bytes(b):
    return base64.b64encode(b).decode()


def b64encode_str(s):
    return base64.b64encode(s.encode('utf-8')).decode()


def encode_name(s):
    return '=?utf-8?b?%s?=' % b64encode_str(s)
