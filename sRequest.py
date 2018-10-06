# -*- coding: utf-8 -*-

import socket, ssl
from urllib.parse import urlparse

class Structure:
    def __init__(self, headers, status_code, redirects, text):
        self.headers = headers
        self.status_code = status_code
        self.redirects = redirects
        self.text = text

class Elcap():
    default_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        'DNT': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }

    def __init__(self):
        self.url = ''
        self.full = True
        self.read = 64000
        self.headers = {}
        self.history = []
        self.redirects = 0
        self.status_code = ''
        self.encoding = 'ISO-8859-1'

    def format_request(self, host, path, input_data):
        if path == '':
            path = '/'

        output_data = 'GET ' + path + ' HTTP/1.0\r\n' \
            'Host: ' + host + '\r\n'

        for key, value in input_data.items():
            output_data += '{}: {}\r\n'.format(key, value)

        output_data += '\r\n'

        return bytes(output_data, 'utf-8')

    def format_dict(self, input_data):
        output_data = {}

        _tmp = input_data.split('\r\n')
        self.status_code = _tmp[0].replace('HTTP/1.0 ', '')

        del _tmp[0]

        for item in _tmp:
            data = item.split(': ')
            output_data[data[0]] = data[1]

        self.headers = output_data

    def resp_analyz(self):
        try:
            if '301' in self.status_code:
                self.history.append(Structure(self.headers, self.status_code, self.redirects, self.text))
                self.redirects += 1
                self.get(self.headers['Location'], self.full, self.read, self.encoding, self.headers)
        except:
            pass

    def http(self, url, _tmp):
        data = ''

        with socket.create_connection((url.netloc, 80)) as sock:
            sock.sendall(_tmp)

            if self.full:
                while True:
                    part = sock.recv(self.read)
                    data += str(part, self.encoding)

                    if part == b'':
                        break
            else:
                part = sock.recv(self.read)
                data += str(part, self.encoding)

        return data

    def https(self, url, _tmp):
        data = ''
        context = ssl.create_default_context()

        with socket.create_connection((url.netloc, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=url.netloc) as ssock:
                ssock.sendall(_tmp)

                if self.full:
                    while True:
                        part = ssock.recv(self.read)
                        data += str(part, self.encoding)

                        if part == b'':
                            break
                else:
                    part = ssock.recv(self.read)
                    data += str(part, self.encoding)

        return data

    def get(self, url, full=True, read=1024, encoding='ISO-8859-1', headers=default_headers):
        self.url = url
        self.full = full
        self.read = read
        self.encoding = encoding
        self.headers = headers
    
        url = urlparse(url)
        _tmp = self.format_request(url.netloc, url.path, headers)
        
        if url.scheme == 'http':
            data = self.http(url, _tmp)
        elif url.scheme == 'https':
            data = self.https(url, _tmp)

        self.headers, self.text = data.split('\r\n\r\n')
        self.format_dict(self.headers)

        self.resp_analyz()
        
        return self