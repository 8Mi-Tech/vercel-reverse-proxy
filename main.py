from flask import Flask, redirect
from flask_caching import Cache
import httpx

app = Flask(__name__)
cache = Cache(app)

Rootlink = "https://vercel-proxy.zkitefly.eu.org"  # 更改为你的实际站点根链接

app.config['CACHE_TYPE'] = 'simple'
cache.init_app(app)

@app.route('/<path:link>')
@cache.cached(timeout=300)  # 设置缓存过期时间为 300 秒（5 分钟）
def index(link):
    full_link = f"https://{link}" if not link.startswith(('http://', 'https://')) else link
    response = httpx.head(full_link)
    
    if 'Location' not in response.headers:
        return redirect(Rootlink + '/p/' + link)
    else:
        location = response.headers['Location']
        return redirect(Rootlink + '/' + location)

if __name__ == "__main__":
    app.run()
