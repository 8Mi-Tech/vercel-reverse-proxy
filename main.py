import httpx
from flask_caching import Cache
from flask import Flask, abort, Response

app = Flask(__name__)
#cache = Cache(app)
app.config['CACHE_TYPE'] = 'simple'
#cache.init_app(app)

@app.route('/<path:link>')
#@cache.cached(timeout=300)  # 设置缓存过期时间为 300 秒（5 分钟）
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
            head_response.headers['Location'] = f'https://rpdl-vercel.8mi.edu.pl/{full_link}'
            return head_response
        else:
            full_link = head_response.headers['Location']

def request_error_output(request_type, error_type, error_message):
    print(f'{request_type} / {error_type} Error：{error_message}')
    abort(500)

if __name__ == "__main__":
    app.run()
