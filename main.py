from flask import Flask, redirect
from flask_caching import Cache
import httpx

app = Flask(__name__)
cache = Cache(app)

Rootlink = "https://rpdl-vercel.8mi.edu.pl/"  # 注意末尾的斜杠，确保根链接以斜杠结尾

app.config['CACHE_TYPE'] = 'simple'
cache.init_app(app)

@app.route('/<path:link>')
@cache.cached(timeout=300)  # 设置缓存过期时间为 300 秒（5 分钟）
def index(link):
    full_link = f"https://{link}" if not link.startswith(('http://', 'https://')) else link
    response = httpx.head(full_link)

    if 'Location' in response.headers:
        location = response.headers['Location']
        # 处理重定向链上的连续重定向
        while location.startswith(('http://', 'https://')):
            app.logger.info(f"Redirecting to: {location}")
            response = httpx.head(location)
            if 'Location' in response.headers:
                location = response.headers['Location']
            else:
                break  # 如果没有 Location 头，则退出循环
        return redirect(f"{Rootlink}{location}")  # 在根链接和重定向链接之间添加斜杠
    else:
        app.logger.info(f"No 'Location' header found in response for link: {link}")
        return redirect(f"{Rootlink}/{link}")  # 在根链接和路径之间添加斜杠

if __name__ == "__main__":
    app.run()
