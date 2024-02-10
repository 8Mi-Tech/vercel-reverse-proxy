import os
import httpx
from flask_caching import Cache
from flask import Flask, abort

app = Flask(__name__)
cache = Cache(app)
app.config['CACHE_TYPE'] = 'simple'
cache.init_app(app)
@app.route('/<path:link>')
@cache.cached(timeout=300)  # 设置缓存过期时间为 300 秒（5 分钟）

def index(link):
    if link == 'favicon.ico':
        abort(404)
    full_link = f"https://{link}" if not link.startswith(('http://', 'https://')) else link
    while True: 
        response = httpx.head(full_link,resolvers=['8.8.8.8'])
        if 'Location' not in response.headers:
            return httpx.get(full_link, resolvers=['8.8.8.8'], timeout=10)
        else:
            full_link = response.headers['Location']
    
if __name__ == "__main__":
    app.run()
