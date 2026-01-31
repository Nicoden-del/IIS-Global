import feedparser
from google import genai
import os
from datetime import datetime

# 配置 Gemini API（使用 v1 稳定版本，不使用过时的 v1beta）
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("请设置 GEMINI_API_KEY 环境变量")

# 使用 v1 API，模型使用当前稳定的 gemini-2.5-flash
_client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options={"api_version": "v1"},
)

# Google News RSS 源（中文新闻）
GOOGLE_NEWS_RSS = "https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans"

def fetch_news():
    """抓取 Google News"""
    print("正在抓取 Google News...")
    feed = feedparser.parse(GOOGLE_NEWS_RSS)
    
    news_items = []
    for entry in feed.entries[:10]:  # 获取前10条新闻
        news_items.append({
            'title': entry.title,
            'link': entry.link,
            'published': entry.get('published', '未知时间')
        })
    
    return news_items

def summarize_with_gemini(news_items):
    """使用 Gemini 总结新闻（v1 API + gemini-2.5-flash）"""
    print("正在使用 Gemini 总结新闻...")
    
    # 构建提示词
    news_text = "\n".join([f"{i+1}. {item['title']}" for i, item in enumerate(news_items)])
    prompt = f"""请用中文总结以下新闻标题，提取主要话题和趋势：

{news_text}

请提供一个简洁的总结（3-5句话）。"""
    
    # 调用 Gemini（v1 稳定版，模型：gemini-2.5-flash）
    response = _client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text

def generate_html(news_items, summary):
    """生成 HTML 页面"""
    print("正在生成 HTML...")
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    news_html = ""
    for item in news_items:
        news_html += f"""
        <div class="news-item">
            <h3><a href="{item['link']}" target="_blank">{item['title']}</a></h3>
            <p class="time">{item['published']}</p>
        </div>
        """
    
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google News 新闻摘要</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .update-time {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        
        .summary {{
            background: #f8f9fa;
            padding: 30px;
            border-left: 5px solid #667eea;
            margin: 30px;
            border-radius: 10px;
        }}
        
        .summary h2 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.5em;
        }}
        
        .summary p {{
            color: #555;
            line-height: 1.8;
        }}
        
        .news-list {{
            padding: 0 30px 30px;
        }}
        
        .news-list h2 {{
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        
        .news-item {{
            padding: 20px;
            margin-bottom: 15px;
            background: #fff;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            transition: all 0.3s ease;
        }}
        
        .news-item:hover {{
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
            transform: translateY(-2px);
        }}
        
        .news-item h3 {{
            margin-bottom: 8px;
        }}
        
        .news-item a {{
            color: #667eea;
            text-decoration: none;
            font-size: 1.1em;
        }}
        
        .news-item a:hover {{
            color: #764ba2;
            text-decoration: underline;
        }}
        
        .time {{
            color: #999;
            font-size: 0.9em;
        }}
        
        footer {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📰 Google News 新闻摘要</h1>
            <p class="update-time">最后更新：{now}</p>
        </header>
        
        <div class="summary">
            <h2>🤖 AI 总结</h2>
            <p>{summary}</p>
        </div>
        
        <div class="news-list">
            <h2>📋 新闻列表</h2>
            {news_html}
        </div>
        
        <footer>
            <p>由 Gemini 自动生成 | 数据来源：Google News</p>
        </footer>
    </div>
</body>
</html>
"""
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ HTML 文件已生成：index.html")

def main():
    try:
        # 1. 抓取新闻
        news_items = fetch_news()
        print(f"✅ 成功抓取 {len(news_items)} 条新闻")
        
        # 2. 使用 Gemini 总结
        summary = summarize_with_gemini(news_items)
        print(f"✅ AI 总结完成")
        
        # 3. 生成 HTML
        generate_html(news_items, summary)
        
        print("\n🎉 全部完成！")
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        raise

if __name__ == "__main__":
    main()
