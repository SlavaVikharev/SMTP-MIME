import ssl
import sys
import socket
import select

log = sys.stderr.write


CR = b'\r'
LF = b'\n'
CRLF = CR + LF


class SMTP:
    def __init__(self, host, port, ssl_):
        self.host = host
        self.port = port
        self.ssl_ = ssl_

        self.sock = socket.create_connection((self.host, self.port))
        self.make_file()

        if self.ssl_:
            self.ssl_wrap()

        self.get_resp()
        self.extensions = self.parse_exts(self.send('EHLO hello'))
        self.auth_types = self.get_auth_types()

        if 'starttls' in self.extensions:
            self.send('STARTTLS')
            self.ssl_wrap()

        self.send('EHLO hello')

    def make_file(self):
        self.file = self.sock.makefile('rb')

    def ssl_wrap(self):
        self.sock = ssl.wrap_socket(self.sock)
        self.make_file()

    def parse_exts(self, ehlo_res):
        return {ext[4:].lower() for ext in ehlo_res.splitlines()}

    def get_auth_types(self):
        auth = filter(lambda ext: ext.startswith('auth'), self.extensions)
        auth = list(auth)
        if not auth:
            return None
        auth = auth[0]
        return set(auth.split()[1:])

    def get_resp(self):
        line = self.file.readline().decode()
        if line.startswith(('5', '4')):
            raise ConnectionError(line)
        resp = [line]
        while line and line[3] == '-':
            line = self.file.readline().decode()
            resp.append(line)
        resp = ''.join(resp)
        log('<=\n%s' % resp)
        return resp

    def send_bytes(self, line):
        self.sock.send(line + CRLF)

    def send_string(self, line, log_=True):
        log('=>\n')
        if log_:
            log('%s\n' % line)
        self.send_bytes(line.encode())

    def send(self, text, log_=True):
        self.send_string(text, log_)
        return self.get_resp()

    def send_pipelining(self, parts):
        log('=>\n')
        for part in parts:
            if part[1]:
                log('%s\n' % part[0])
        self.send_string('\r\n'.join(map(lambda x: x[0], parts)), log_=False)
        for part in parts:
            self.get_resp()
