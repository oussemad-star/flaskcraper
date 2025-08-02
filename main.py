from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse

app = Flask(__name__)

@app.route('/')
def hello():
    return "✅ Flask Article Extractor is Running!"

@app.route('/extract', methods=['POST'])
def extract_article():
    try:
        data = request.get_json(force=True)
        print("📥 Received data:", data)

        url = data.get('url')
        if not url:
            print("❌ No URL provided.")
            return jsonify({"error": "Missing URL"}), 400

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        article_text = ' '.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

        title = soup.title.string.strip() if soup.title and soup.title.string else "No title"
        domain = urlparse(url).netloc.replace('www.', '')

        print("✅ Extraction successful:", {"title": title, "domain": domain})
        return jsonify({
            'title': title,
            'domain': domain,
            'url': url,
            'content': article_text
        })

    except Exception as e:
        print("❌ Exception occurred:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
