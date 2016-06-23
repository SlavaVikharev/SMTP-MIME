import sys
import ssl
import base64
import getpass
import argparse
from smtp import SMTP, NotSmtpServer
from b64ext import *
from generator import gen_message


parser = argparse.ArgumentParser()
parser.add_argument('host', type=str,
                    help='SMTP server host')
parser.add_argument('port', type=int,
                    help='SMTP server port')
parser.add_argument('--ssl', action='store_true',
                    help='Use ssl')
parser.add_argument('--auth', action='store_true',
                    help='Use authorization')
parser.add_argument('--fromname', type=str, default='From',
                    help='Sender name')
parser.add_argument('--fromemail', type=str, default='a@a.com',
                    help='youremail@example.com')
parser.add_argument('--toname', type=str, default='To',
                    help='Receiver name')
parser.add_argument('toemail', type=str,
                    help='Receiver email')
parser.add_argument('--dir', type=str, default='.',
                    help='Directory with images')
args = parser.parse_args()


try:
    smtp = SMTP(args.host, args.port, args.ssl)
except ssl.SSLError as e:
    print('Check smtp port and ssl bool')
    sys.exit()
except NotSmtpServer as e:
    print(e)
    sys.exit()

if '8bitmime' not in smtp.extensions:
    args.fromname = encode_name(args.fromname)
    args.toname = encode_name(args.toname)

message = gen_message(args.dir, **args.__dict__)

try:
    to_send_parts = []

    if args.auth:
        types = smtp.auth_types

        auth_type = None

        if not (types and ('login' in types or 'plain' in types)):
            print('WARNING: There is no opportunity to authenticate...')
        elif 'login' in types:
            auth_type = 'login'
        elif 'plain' in types:
            auth_type = 'plain'

        if auth_type is not None:
            smtp.send('AUTH %s' % auth_type.upper())

            user = input('Your username:\n')
            passw = getpass.getpass('Your password:\n')

            user = b64encode_str(user)
            passw = b64encode_str(passw)

            smtp.send(user, log_=False)
            smtp.send(passw, log_=False)

    to_send_parts.append(('MAIL FROM: <%s>' % args.fromemail, True))
    to_send_parts.append(('RCPT TO: <%s>' % args.toemail, True))

    if 'pipelining' in smtp.extensions:
        smtp.send_pipelining(to_send_parts)
    else:
        lam = lambda p: smtp.send(p[0], log_=p[1])
        list(map(lam, to_send_parts))

    smtp.send('DATA')
    smtp.send(message, log_=False)

except ConnectionError as e:
    print('\nThe error has been occured!')
    print(e)
finally:
    try:
        smtp.send('QUIT')
    except ConnectionError as e:
        print('Error during quit')
        print(e)
