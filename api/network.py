from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from ujson import dumps

class handler(BaseHTTPRequestHandler):
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
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(dumps(opt).encode(encoding='UTF-8'))
        return

    def do_GET(self):
        self.action()

    def do_HEAD(self):
        self.action()

    def do_POST(self):
        self.action()

    def do_PUT(self):
        self.action()

    def do_DELETE(self):
        self.action()

    def do_CONNECT(self):
        self.action()

    def do_OPTIONS(self):
        self.action()

    def do_TRACE(self):
        self.action()

    def do_PATCH(self):
        self.action()

    def do_PROFIND(self):
        self.action()
