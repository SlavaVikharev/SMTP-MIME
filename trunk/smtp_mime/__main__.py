import sys
import ssl
import json
import base64
from smtp import SMTP
from b64ext import b64encode_str
from generator import gen_message


def check_settings(settings):
    return ('images_dir' in settings and
            'host' in settings and
            'port' in settings and
            'from_name' in settings and 
            'from_email' in settings and
            'to_name' in settings and
            'to_email' in settings)


SETTINGS_FILENAME = 'settings.json'

try:
    with open(SETTINGS_FILENAME) as f:
        settings = json.load(f)
except OSError:
    print('Cannot find %s' % SETTINGS_FILENAME)
    sys.exit()
except json.JSONDecodeError:
    print('%s is not valid' % SETTINGS_FILENAME)
    sys.exit()

if not check_settings(settings):
    print('Incorrect settings, please fix it, there is a template')
    sys.exit()

message = gen_message(settings['images_dir'], **settings)

host, port = settings['host'], settings['port']

try:
    smtp = SMTP(host, port, settings.get('ssl', False))
except ssl.SSLError as e:
    print('Check smtp port and ssl bool')
    sys.exit()

try:
    if 'user' in settings:
        smtp.send('AUTH LOGIN')

        smtp.send(b64encode_str(settings['user']), log_=False)
        smtp.send(b64encode_str(settings.get('password', '')), log_=False)

    smtp.send('MAIL FROM: <%s>' % settings['from_email'])
    smtp.send('RCPT TO: <%s>' % settings['to_email'])

    smtp.send('DATA')

    smtp.send(message, log_=False)
except ConnectionError as e:
    print('The error was occured!')
    print(e)
finally:
    try:
        smtp.send('QUIT')
    except ConnectionError as e:
        print('Error during quit')
        print(e)
