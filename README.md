# Nahida.♡二次元随机图 接口/抽卡模块
![maven](https://img.shields.io/badge/Python-blue)
![maven](https://img.shields.io/badge/Vercel-black)
![maven](https://img.shields.io/badge/Nahida.♡-green)<br>
一个使用Python编写的运行在Vercel的随机图接口（需自备图片链接）<br>
### 简介
本项目支持使用Vercel搭建，您可以Fork本仓库后访问 [Vercel](https://vercel.com) 使用GitHub登录并导入您的Fork仓库在根目录创建Project。<br>
<br>
随机图链接添加方法：将 图片集名称.txt 上传到/data文件夹，txt内每一行是一条图片链接。<br>
内置的 [data/public.txt](https://github.com/ZiAzusa/nahida-random-image/blob/main/data/public.txt) 来自 [MirlKoi图库](https://iw233.cn) 在群文件公开的数据，链接为新浪图床，酌情使用。<br>
<br>
本项目支持24小时内调用限制和速率限制，您可以打开 [api/random.py](https://github.com/ZiAzusa/nahida-random-image/blob/main/api/random.py) 进行相关配置<br>
注意！！若要使用24小时内调用限制，需要使用Redis数据库，并在Vercel的环境变量配置以下信息：<br>
| 键 | 值 |
| --- | --- |
|REDIS_HOST|您的Redis数据库地址|
|REDIS_PORT|您的Redis数据库端口|
|REDIS_PWD|您的Redis数据库密码|

若您的Redis数据库空间极为有限，建议设置<b>Data eviction policy</b>为<b>allkeys-lru</b>
### 其他说明
具体使用方法请参考 [Nahida.♡二次元随机图](https://imgapi.nahida.xin/help)<br>
将域名替换为您的Vercel域名即可<br>
P.S.本意是只想收集亿些小纳西妲的图的，不知不觉就…阿巴阿巴~

---

Made with ♡ by [魂归梓里(ZiAzusa)](https://about.sukimoe.cn/)
