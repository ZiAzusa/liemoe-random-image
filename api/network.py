from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from ujson import dumps
import socket

class handler(BaseHTTPRequestHandler):
    def handle_request(self, content_type, opt):
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.end_headers()
        self.wfile.write(opt.encode(encoding='UTF-8'))
        return
    
    def action(self):
        url = 'https://www.example.com' + self.path
        ipt = parse_qs(urlparse(url).query)
        expect = ipt.get('expect', [None])[0]
        if expect == "ip":
            self.handle_request('text/plain', self.headers['x-real-ip'])
            return
        elif expect == "ua":
            self.handle_request('text/plain', self.headers['user-agent'])
            return
        elif expect == "time":
            self.handle_request('text/plain', self.date_time_string())
            return
        opt = {
            'status'  : 200,
            'time'    : self.date_time_string(),
            'ip'      : self.headers['x-real-ip'],
            'path'    : self.path,
            'method'  : self.command,
            'http_ver': self.request_version,
            'server'  : {
                'host': self.client_address[0],
                'port': self.client_address[1],
                'ver' : self.version_string()
            },
            'headers' : {}
        }
        opt['headers'] = dict(sorted(self.headers.items(), key=lambda v:v[0]))
        opt['headers'].pop("forwarded", None)
        opt['headers'].pop("x-vercel-proxy-signature", None)
        opt['headers'].pop("x-vercel-proxy-signature-ts", None)
        self.handle_request('application/json', dumps(opt))
        return

    def handle_one_request(self):
        try:
            self.raw_requestline = self.rfile.readline(65537)
            if len(self.raw_requestline) > 65536:
                self.send_error(414)
                return
            if not self.raw_requestline:
                self.close_connection = True
                return
            if not self.parse_request():
                return
            self.action()
            self.wfile.flush()
        except socket.timeout as e:
            self.log_error("Request timed out: %r", e)
            self.close_connection = True
        return
