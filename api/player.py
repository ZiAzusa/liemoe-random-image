from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = "https://www.example.com" + self.path
        input_data = parse_qs(urlparse(url).query)
        time = input_data.get("time", ["10"])[0]
        if time.isdigit():
            time = int(time)
        else:
            time = 10
        warning = ''
        if time < 5:
            time = 10
            warning = '<script>console.log("警告：time值应大于等于5！已修改为默认值（10）");</script>'
        time = str(time * 1000)
        opt = '<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width,user-scalable=0"></head><body><div class="g o"></div><div class=g></div><style>.g{-webkit-transition:opacity 1s;-moz-transition:opacity 1s;-ms-transition:opacity 1s;-o-transition:opacity 1s;transition:opacity 1s;position:fixed;height:100%;width:100%;opacity:0;left:0;top:0}.g.o{opacity:1}</style><style id=r></style>' + warning + '<script>const a=()=>{fetch("random?type=text&"+t++).then(b=>{if(b.status==200){return b.text()}else throw"Error,See: http://"+location.hostname+"/random?only_check=true"}).then(c=>{let e=document.querySelectorAll(".g");for(i=0;i<e.length;i++)e[i].classList.toggle("o");document.getElementById("r").innerText=\'.g{background:url(\'+d[0]+\') no-repeat center 0/cover}.g.o{background:url(\'+d[1]+\') no-repeat center 0/cover}\';(new Image).src=c;d[0]=d[1];d[1]=c});return a};var d=["","random"];var t=0;setInterval(a(),' + time + ')</script></body></html>'
        self.send_response(200)
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type,Content-Length,Accept-Encoding,X-Requested-with,Origin')
        self.send_header('Access-Control-Allow-Methods', 'GET,HEAD,OPTIONS')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'text/html;charset=utf-8')
        self.end_headers()
        self.wfile.write(opt.encode(encoding='UTF-8'))
        return
