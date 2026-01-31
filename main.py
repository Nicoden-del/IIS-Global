import os, feedparser, datetime
import google.generativeai as genai

def run():
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')
    feed = feedparser.parse("https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U00xOXRia0U2R2dKTVVpZ0FQAQ?ceid=US:en&oc=3")
    
    html = f"<html><body style='background:#000;color:#0f0;padding:50px;'><h1>🛡️ IIS TERMINAL</h1><p>Update: {datetime.datetime.now()}</p><hr>"
    for entry in feed.entries[:3]:
        try:
            res = model.generate_content(f"总结这条新闻: {entry.title}")
            html += f"<div><h3>{entry.title}</h3><p>{res.text}</p></div>"
        except: continue
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html + "</body></html>")

if __name__ == "__main__":
    run()
