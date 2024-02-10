import os
import httpx
import socket
from flask_caching import Cache
from flask import Flask, abort, Response

app = Flask(__name__)
cache = Cache(app)
app.config['CACHE_TYPE'] = 'simple'
cache.init_app(app)

@app.route('/<path:link>')
@cache.cached(timeout=300)  # 设置缓存过期时间为 300 秒（5 分钟）
def index(link):
    if link == 'favicon.ico':
        abort(404)
    
    temp_link = f"https:/{link}" if not link.startswith(('http:/', 'https:/')) else link # 第一步，安抚Vercel的情绪
    if 'https:/' in temp_link:
        full_link = temp_link.replace('https:/', 'https://')
    elif 'http:/' in temp_link:
        full_link = temp_link.replace('http:/', 'http://')
    else:
        abort(500)
    
    # 保存HEAD请求的信息
    head_response = None
    while True: 
        print(f'HEAD Connection：{full_link}')
        try:
            head_response = httpx.head(full_link)
        except httpx.ConnectError as e:
            request_error_output("HEAD","Connect",e)
        except httpx.RequestError as e:
            request_error_output("HEAD","Request",e)
        except Exception as e:
            request_error_output("HEAD","Unknown",e)
        
        if 'Location' not in head_response.headers:
            print(f'GET Connection：{full_link}')
            try:
                response_get = httpx.get(full_link, timeout=10)
                # 生成流式响应
                def generate():
                    for chunk in response_get.iter_bytes():
                        yield chunk
                
                # 构造包含HEAD信息的响应
                response = Response(generate(), mimetype='application/octet-stream')
                # 添加HEAD请求的响应头部信息到响应中
                for header, value in head_response.headers.items():
                    response.headers[header] = value
                return response
            except httpx.ConnectError as e:
                request_error_output("GET","Connect",e)
            except httpx.RequestError as e:
                request_error_output("GET","Request",e)
            except Exception as e:
                request_error_output("GET","Unknown",e)
            break
        else:
            full_link = head_response.headers['Location']

def request_error_output(request_type, error_type, error_message):
    print(f'{request_type} / {error_type} Error：{error_message}')
    abort(500)

if __name__ == "__main__":
    app.run()
