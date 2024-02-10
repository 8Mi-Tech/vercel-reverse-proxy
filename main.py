import os
import httpx
import socket
from flask_caching import Cache
from flask import Flask, abort, make_response, jsonify

app = Flask(__name__)
cache = Cache(app)
app.config['CACHE_TYPE'] = 'simple'
cache.init_app(app)

@app.route('/<path:link>')
@cache.cached(timeout=300)  # 设置缓存过期时间为 300 秒（5 分钟）
def index(link):
    with httpx.Client() as client:
        if link == 'favicon.ico':
            abort(404)
        
        temp_link = f"https:/{link}" if not link.startswith(('http:/', 'https:/')) else link # 第一步，安抚Vercel的情绪
        if 'https:/' in temp_link:
            full_link = temp_link.replace('https:/', 'https://')
        elif 'http:/' in temp_link:
            full_link = temp_link.replace('http:/', 'http://')
        else:
            abort(500)
        
        while True: 
            print(f'HEAD Connection：{full_link}')
            try:
                response_head = client.head(full_link)
            except httpx.ConnectError as e:
                request_error_output("HEAD","Connect",e)
            except httpx.RequestError as e:
                request_error_output("HEAD","Request",e)
            except Exception as e:
                request_error_output("HEAD","Unknown",e)
            
            if 'Location' not in response_head.headers:
                print(f'GET Connection：{full_link}')
                try:
                    response_get = client.get(full_link, timeout=10, headers=response_head.headers)

                    flask_response = make_response(response_get.content)
                    flask_response.status_code = response_get.status_code
                    for header, value in response.headers.items():
                        flask_response.headers[header] = value
                    return flask_response
                except httpx.ConnectError as e:
                    request_error_output("GET","Connect",e)
                except httpx.RequestError as e:
                    request_error_output("GET","Request",e)
                except Exception as e:
                    request_error_output("GET","Unknown",e)
            else:
                full_link = response_head.headers['Location']
    
def request_error_output(request_type, error_type, error_message):
    print(f'{request_type} / {error_type} Error：{error_message}')
    abort(500)

if __name__ == "__main__":
    app.run()
