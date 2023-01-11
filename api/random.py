from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from time import time, gmtime, strftime
from json import loads, dumps
from os import path, listdir
from random import choice

fileList = listdir(path.join("data", ""))
sortList = [i.replace(".txt", "") for i in fileList]

def cache(func):
    cache_data = {}
    def run_func(*args, **kwargs):
        key = ".".join(args)
        value = cache_data.get(key, None)
        if value == None:
            value = func(*args, **kwargs)
            cache_data[key] = value
        return choice(value).strip()
    return run_func

@cache
def read_data(sort):
    with open(path.join("data", sort + ".txt"), encoding='utf-8') as file:
        data = file.readlines()
    return data

def report_error(title, code, note, tip, text):
    return('<html class="no-js" lang="zh-CN"><head><title>' + title + '</title><meta charset="UTF-8"><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><meta http-equiv="X-UA-Compatible" content="IE=Edge"><meta name="robots" content="noindex, nofollow"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="shortcut icon" href="style/favicon.ico"><link rel="stylesheet" id="cf_styles-css" href="style/css/repoeter.css"><style>body{color:black;background-color:white}@media (prefers-color-scheme:dark){body{color:white;background-color:#1A1A1A}.text-black-dark{color:#BFBFBF}}</style></head><body><div id="cf-wrapper"><div id="cf-error-details" class="p-0"><header class="mx-auto pt-10 lg:pt-6 lg:px-8 w-240 lg:w-full mb-15 antialiased"><h1 class="inline-block md:block mr-2 md:mb-2 font-light text-60 md:text-3xl text-black-dark leading-tight"><span data-translate="error">' + code + '</span></h1><h2 class="text-gray-600 leading-1.3 text-3xl lg:text-2xl font-light">' + note + '</h2></header><section class="w-240 lg:w-full mx-auto mb-8 lg:px-8"><div id="what-happened-section" class="w-1/2 md:w-full"><h2 class="text-3xl leading-tight font-normal mb-4 text-black-dark antialiased" data-translate="what_happened">' + tip + '</h2><p>' + text + '</p></div></section><div class="cf-error-footer cf-wrapper w-240 lg:w-full py-10 sm:py-4 sm:px-8 mx-auto text-center sm:text-left border-solid border-0 border-t border-gray-300"><p class="text-13"><span class="cf-footer-item sm:block sm:mb-1"><span>2022-2023: Nahida.Fun</span></span></p></div></div></div></body></html>')

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        input_header = self.headers
        userip = input_header.get("X-User-IP")
        url = "http://127.0.0.1" + self.path
        input_data = parse_qs(urlparse(url).query)
        setSort = input_data.get("sort", ['random'])[0]
        if setSort == "random":
            setSort = choice(sortList)
        elif setSort not in sortList:
            self.send_response(404)
            self.send_header('Content-type', 'text/html;charset=utf-8')
            self.end_headers()
            opt = report_error("请求失败", "404 Not Found", "您请求的资源不存在。", "发生什么了？", "您提交的sort参数不合法")
            self.wfile.write(opt.encode(encoding='UTF-8'))
            return
        setType = input_data.get("type", [None])[0]
        setNum = input_data.get("num", ["1"])[0]
        if setNum.isdigit():
            setNum = int(setNum)
        else:
            setNum = 0
        if setNum == 1 and not setType == "json":
            opt = read_data(setSort)
        elif setNum > 100 or setNum < 1:
            self.send_response(403)
            self.send_header('Content-type', 'text/html;charset=utf-8')
            self.end_headers()
            opt = report_error("请求失败", "400 Bad Request", "我无法理解您的请求。", "发生什么了？", "您提交的num参数不合法")
            self.wfile.write(opt.encode(encoding='UTF-8'))
            return
        else:
            pic = []
            for i in range(setNum):
                pic.append(read_data(setSort))
            opt = dumps({"pic": pic})
            setType = "json"
        if setType == "text":
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain;charset=utf-8')
        elif setType == "json":
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
        else:
            self.send_response(302)
            self.send_header('Location', opt)
        self.end_headers()
        self.wfile.write(opt.encode(encoding='UTF-8'))
        return
