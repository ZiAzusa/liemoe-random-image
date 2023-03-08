from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from time import time, gmtime, strftime
from os import path, environ, listdir
from ujson import loads, dumps
from random import choice
import redis

#配置项，以下配置设置小于等于0则为无限制
#每IP每24小时最大请求链接数（需要在环境变量配置Redis信息）
maxNum = 0
#速率限制：每IP每limitTime秒可以请求limitFrequency次API
limitTime = 5
limitFrequency = 3

if maxNum > 0 and environ.get("REDIS_HOST", False) and environ.get("REDIS_PORT", False) and environ.get("REDIS_PWD", False):
    connection = redis.ConnectionPool(
        host=environ.get("REDIS_HOST"),
        port=environ.get("REDIS_PORT"),
        password=environ.get("REDIS_PWD"),
        decode_responses=True,
        health_check_interval=30
    )
    redisRes = redis.StrictRedis(connection_pool=connection)
    with24hLimit = True
else:
    with24hLimit = False
if limitFrequency > 0 and limitTime > 0:
    withSpeedLimit = True
else:
    withSpeedLimit = False
fileList = listdir(path.join("data", ""))
sortList = [i.replace(".txt", "") for i in fileList]
thumbnail = False

def check_ip(ip, num):
    if not with24hLimit:
        return [-1, "1970-01-01 00:00:00"]
    redisData = redisRes.get(ip)
    nowTime = time()
    if redisData == None:
        value = {'frequency': 0, 'time': nowTime}
        redisRes.set(ip, dumps(value))
    else:
        value = loads(redisData)
        if nowTime >= value['time'] + 86400:
            value = {'frequency': 0, 'time': nowTime}
            redisRes.set(ip, dumps(value))
    if value['frequency'] <= maxNum:
        value['frequency'] = value['frequency'] + num
        redisRes.set(ip, dumps(value))
    if value['frequency'] <= (maxNum + 100) and value['frequency'] > maxNum:
        value['frequency'] = (maxNum + 101)
        redisRes.set(ip, dumps(value))
        remain_time = value['time'] + 86400 - nowTime
        m, s = divmod(remain_time, 60)
        h, m = divmod(m, 60)
        return [value['frequency'], "%02d:%02d:%02d" % (h, m, s)]
    elif value['frequency'] > (maxNum + 100):
        remain_time = value['time'] + 86400 - nowTime
        m, s = divmod(remain_time, 60)
        h, m = divmod(m, 60)
        return [value['frequency'], "%02d:%02d:%02d" % (h, m, s)]
    timeArray = gmtime(value['time'])
    styleTime = strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return [value['frequency'], styleTime]

def report_error(title, code, note, tip, text):
    return('<html class="no-js" lang="zh-CN"><head><title>' + title + '</title><meta charset="UTF-8"><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><meta http-equiv="X-UA-Compatible" content="IE=Edge"><meta name="robots" content="noindex, nofollow"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="shortcut icon" href="style/favicon.ico"><link rel="stylesheet" id="cf_styles-css" href="/style/css/report.min.css"><style>body{color:black;background-color:white}@media (prefers-color-scheme:dark){body{color:white;background-color:#1A1A1A}.text-black-dark{color:#BFBFBF}}</style></head><body><div id="cf-wrapper"><div id="cf-error-details" class="p-0"><header class="mx-auto pt-10 lg:pt-6 lg:px-8 w-240 lg:w-full mb-15 antialiased"><h1 class="inline-block md:block mr-2 md:mb-2 font-light text-60 md:text-3xl text-black-dark leading-tight"><span data-translate="error">' + code + '</span></h1><h2 class="text-gray-600 leading-1.3 text-3xl lg:text-2xl font-light">' + note + '</h2></header><section class="w-240 lg:w-full mx-auto mb-8 lg:px-8"><div id="what-happened-section" class="w-1/2 md:w-full"><h2 class="text-3xl leading-tight font-normal mb-4 text-black-dark antialiased" data-translate="what_happened">' + tip + '</h2><p>' + text + '</p></div></section></div></div></body></html>')

def cache(func):
    cache_data = {}
    def run_func(*args, **kwargs):
        key = ".".join(args)
        value = cache_data.get(key, None)
        if value == None:
            value = func(*args, **kwargs)
            cache_data[key] = value
        if thumbnail:
            return choice(value).strip() + "?thumbnail=" + thumbnail
        return choice(value).strip()
    return run_func

@cache
def read_data(sort):
    with open(path.join("data", sort + ".txt"), encoding='utf-8') as file:
        data = file.readlines()
    return data

def limit_cache(func):
    limit_data = {}
    def run_func(*args, **kwargs):
        limit_key = ".".join(args)
        limit_value = limit_data.get(limit_key, None)
        if limit_value == None:
            limit_value = func(*args, **kwargs)
        if time() > limit_value['time'] + limitTime:
            limit_value = func(*args, **kwargs)
        limit_value['frequency'] += 1
        limit_data[limit_key] = limit_value
        if limit_value['frequency'] > limitFrequency:
            return True
        return False
    return run_func

@limit_cache
def limit(ip):
    return({'frequency': 0, 'time': time()})

class handler(BaseHTTPRequestHandler):
    def handle_request(self, code, content_type, remain_num, opt):
        self.send_response(code)
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type,Content-Length,Accept-Encoding,X-Requested-with,Origin')
        self.send_header('Access-Control-Allow-Methods', 'GET,HEAD,OPTIONS')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', content_type)
        if remain_num:
            self.send_header('X-Remain-Num', remain_num)
        self.end_headers()
        self.wfile.write(opt.encode(encoding='UTF-8'))
        return

    def do_GET(self):
        global maxNum, thumbnail
        input_header = self.headers
        userip = input_header.get("X-Real-IP")
        if not with24hLimit:
            maxNum = 0
        if withSpeedLimit:
            if limit(userip):
                opt = report_error("速率限制", "429 Too Many Requests", "您请求速度太快啦！", "发生什么了？", "您IP [" + userip + "] 在" + str(limitTime) + "秒内请求次数超过了" + str(limitFrequency) + "次，请稍后再试。")
                self.handle_request(429, 'text/html;charset=utf-8', None, opt)
                return
        url = "https://www.example.com" + self.path
        input_data = parse_qs(urlparse(url).query)
        only_check = input_data.get("only_check", [False])[0]
        if only_check:
            ip_block = check_ip(userip, 0)
            if ip_block[0] > maxNum:
                opt = report_error("检查额度", "200 OK", "您的请求已成功执行。", "执行结果：", "您IP [" + userip + "] 今日额度已用尽<br>距离恢复" + str(maxNum) + "可用额度还有：" + ip_block[1])
            else:
                opt = report_error("检查额度", "200 OK", "您的请求已成功执行。", "执行结果：", "您IP [" + userip + "] 今日额度剩余：" + str(maxNum - ip_block[0]) + "<br>计数周期开始于：" + ip_block[1] + " UTC+0")
            self.handle_request(200, 'text/html;charset=utf-8', (maxNum - ip_block[0]), opt)
            return
        setSort = input_data.get("sort", ['random'])[0]
        if setSort == "random":
            setSort = choice(sortList)
        elif setSort not in sortList:
            opt = report_error("请求失败", "404 Not Found", "您请求的资源不存在。", "发生什么了？", "您提交的sort参数不合法")
            self.handle_request(404, 'text/html;charset=utf-8', None, opt)
            return
        setType = input_data.get("type", [None])[0]
        setNum = input_data.get("num", ["1"])[0]
        if setNum.isdigit():
            setNum = int(setNum)
        else:
            setNum = 0
        thumbnail = input_data.get("thumbnail", [False])[0]
        if setNum == 1 and not setType == "json":
            ip_block = check_ip(userip, 1)
            if ip_block[0] > maxNum:
                opt = report_error("访问受限", "403 Forbidden", "您无权使用。", "发生什么了？", "您IP [" + userip + "] 今日额度已用尽<br>距离恢复" + str(maxNum) + "可用额度还有：" + ip_block[1])
                self.handle_request(403, 'text/html;charset=utf-8', (maxNum - ip_block[0]), opt)
                return
            opt = read_data(setSort)
        elif setNum > 100 or setNum < 1:
            opt = report_error("请求失败", "400 Bad Request", "我无法理解您的请求。", "发生什么了？", "您提交的num参数不合法")
            self.handle_request(400, 'text/html;charset=utf-8', None, opt)
            return
        else:
            ip_block = check_ip(userip, setNum)
            if ip_block[0] > maxNum + setNum:
                opt = report_error("访问受限", "403 Forbidden", "您无权使用。", "发生什么了？", "您IP [" + userip + "] 今日额度已用尽<br>距离恢复" + str(maxNum) + "可用额度还有：" + ip_block[1])
                self.handle_request(403, 'text/html;charset=utf-8', (maxNum - ip_block[0]), opt)
                return
            elif ip_block[0] > maxNum and ip_block[0] <= maxNum + setNum:
                setNum = setNum + maxNum - ip_block[0]
            pic = []
            for i in range(setNum):
                pic.append(read_data(setSort))
            if maxNum + ip_block[0] < 0:
                ip_block[0] = maxNum
            opt = dumps({"pic": pic,  "remain_num": maxNum - ip_block[0]})
            setType = "json"
        if setType == "text":
            self.handle_request(200, 'text/plain;charset=utf-8', (maxNum - ip_block[0]), opt)
        elif setType == "json":
            self.handle_request(200, 'application/json', (maxNum - ip_block[0]), opt)
        else:
            self.send_response(302)
            self.send_header('Access-Control-Allow-Credentials', 'true')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type,Content-Length,Accept-Encoding,X-Requested-with,Origin')
            self.send_header('Access-Control-Allow-Methods', 'GET,HEAD,OPTIONS')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Location', opt)
            self.send_header('X-Remain-Num', (maxNum - ip_block[0]))
            self.end_headers()
        return
