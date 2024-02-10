import os
import httpx
import socket
from flask_caching import Cache
from flask import Flask, abort

app = Flask(__name__)
cache = Cache(app)
app.config['CACHE_TYPE'] = 'simple'
cache.init_app(app)

# 设置自定义的 DNS 服务器地址
def set_dns(dns_ip):
    # 使用自定义的 DNS 服务器地址
    if isinstance(dns_ip, str):
        dns_ip = [dns_ip]
    socket.dnsservers = dns_ip
# 设置自定义 DNS 服务器
custom_dns = '8.8.8.8'  # 例如，设置 Google Public DNS
set_dns(custom_dns)

@app.route('/<path:link>')
@cache.cached(timeout=300)  # 设置缓存过期时间为 300 秒（5 分钟）
def index(link):
    with httpx.Client() as client:
        if link == 'favicon.ico':
            abort(404)
        full_link = f"https://{link}" if not link.startswith(('http://', 'https://')) else link
        while True: 

            try:
                response = client.head(full_link)
            except httpx.ConnectError as e:
                print("HEAD 连接错误:", e)
            except httpx.RequestError as e:
                print("HEAD 请求错误:", e)
            except Exception as e:
                print("HEAD 未知错误:", e)
            
            if 'Location' not in response.headers:
                try:
                    response = client.get(full_link, timeout=10)
                except httpx.ConnectError as e:
                    print("GET 连接错误:", e)
                except httpx.RequestError as e:
                    print("GET 请求错误:", e)
                except Exception as e:
                    print("GET 未知错误:", e)
            else:
                full_link = response.headers['Location']
    
if __name__ == "__main__":
    app.run()
