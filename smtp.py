import ssl
import sys
import socket

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
        if self.ssl_:
            self.ssl_wrap()
            self.get_resp()
        else:
            self.file = self.create_file()
            self.get_resp()
            self.send('EHLO hello')
            self.send('STARTTLS')
            self.ssl_wrap()
        self.send('EHLO hello')

    def ssl_wrap(self):
        self.sock = ssl.wrap_socket(self.sock)
        self.file = self.create_file()

    def create_file(self):
        return self.sock.makefile('rb')

    def get_resp(self, log_=True):
        line = self.file.readline().decode()
        if line.startswith(('5', '4')):
            raise ConnectionError(line)
        resp = [line]
        while line and line[3] == '-':
            line = self.file.readline().decode()
            resp.append(line)
        resp = ''.join(resp)
        if log_:
            log('<=\n%s' % resp)
        return resp

    def send_bytes(self, line):
        self.sock.send(line + CRLF)

    def send_string(self, line, log_=True):
        if log_:
            log('=>\n%s\n' % line)
        self.send_bytes(line.encode())

    def send(self, text, log_=True):
        self.send_string(text, log_)
        return self.get_resp(log_)
