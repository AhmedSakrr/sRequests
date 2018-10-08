# -*- coding: utf-8 -*-

import socket, ssl

try:
    from urllib import quote_plus as encode_params
    from urlparse import urlparse
except:
    from urllib.parse import quote_plus as encode_params
    from urllib.parse import urlparse

class Structure:
    def __init__(self, headers, status_code, redirects, text, url):
        self.headers = headers
        self.status_code = status_code
        self.redirects = redirects
        self.text = text
        self.url = url

class Elcap:
    _get = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        'DNT': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }

    _post = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'close',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache',
        'DNT': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }

    def __init__(self):
        self.encoding = ''
        self.headers = {}
        self.history = []
        self.read = 4096
        self.redirects = 0
        self.url = ''
        self.status_code = ''

    def format_get(self, host, path):
        if path == '':
            path = '/'

        output_data = 'GET ' + path + ' HTTP/1.1\r\n' \
            'Host: ' + host + '\r\n'

        for key, value in self._get.items():
            output_data += '{}: {}\r\n'.format(key, value)

        output_data += '\r\n'

        return bytes(output_data, 'utf-8')

    def format_post(self, host, path, input_data):
        if path == '':
            path = '/'
        
        i = 0
        params = ''
        content_length = len(input_data)-1

        for key, value in input_data.items():
            params += '{}={}'.format(key, value)

            if i != content_length:
                params += '&'

            i += 1

        params = encode_params(params)
        content_length = len(params)

        output_data = 'POST ' + path + ' HTTP/1.1\r\n' \
            'Host: ' + host + '\r\n' \

        for key, value in self._post.items():
            output_data += '{}: {}\r\n'.format(key, value)
        
        output_data += 'Content-Length: {}\r\n\r\n'.format(content_length)
        output_data += params + '\r\n'

        return bytes(output_data, 'utf-8')
        
    def format_dict(self, input_data):
        output_data = {}

        _tmp = input_data.split('\r\n')
        self.status_code = _tmp[0].replace('HTTP/1.0 ', '')
        self.status_code = _tmp[0].replace('HTTP/1.1 ', '')

        del _tmp[0]

        for item in _tmp:
            data = item.split(': ')
            output_data[data[0]] = data[1]

        self.headers = output_data

    def headers_update(self, what, new):
        '''
            what - get|post (str)
            new - new headers. Replace current or add new (dict)
        '''
        if what == 'get':
            for key, value in new.items():
                self._get[key] = value
        elif what == 'post':
            for key, value in new.items():
                self._post[key] = value
        else:
            print('Wrong on inputed method.')

    def resp_analyz(self):
        try:
            if '301' in self.status_code or '302' in self.status_code:
                self.history.append(Structure(self.headers, self.status_code, self.redirects, self.text, self.url))
                self.redirects += 1
                self.get(self.headers['Location'], self.encoding)
        except:
            pass

    def http(self, url, _tmp):
        data = ''

        with socket.create_connection((url.netloc, 80)) as sock:
            sock.sendall(_tmp)

            while True:
                part = sock.recv(self.read)
                data += str(part, self.encoding)

                if part == b'':
                    break

        return data

    def https(self, url, _tmp):
        data = ''
        context = ssl.create_default_context()

        with socket.create_connection((url.netloc, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=url.netloc) as ssock:
                ssock.sendall(_tmp)

                while True:
                    part = ssock.recv(self.read)
                    data += str(part, self.encoding)

                    if part == b'':
                        break

        return data

    def get(self, url, encoding='ISO-8859-1'):
        '''
            Make easy GET request.
                url - link to make request (str)
        '''
        self.url = url
        self.encoding = encoding
    
        url = urlparse(url)
        _tmp = self.format_get(url.netloc, url.path)
        
        if url.scheme == 'http':
            data = self.http(url, _tmp)
        elif url.scheme == 'https':
            data = self.https(url, _tmp)

        data = data.split('\r\n\r\n')
        self.headers = data[0]
        self.text = data[1]

        self.format_dict(self.headers)
        self.resp_analyz()

        return self

    def post(self, url, data, encoding='ISO-8859-1'):
        '''
            Make easy POST request.

                url - link to requests (str)
                data - params to send (dict)
        '''
        self.url = url
        self.encoding = encoding
    
        url = urlparse(url)
        _tmp = self.format_post(url.netloc, url.path, data)

        if url.scheme == 'http':
            data = self.http(url, _tmp)
        elif url.scheme == 'https':
            data = self.https(url, _tmp)

        data = data.split('\r\n\r\n')
        self.headers = data[0]
        self.text = data[1]

        self.format_dict(self.headers)

        return self
