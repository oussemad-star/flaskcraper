from flask import Flask, request, jsonify
from flask_cors import CORS # This line is crucial for handling CORS
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
import logging

# Configure logging for better visibility into server operations
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
# Enable CORS for all origins. In a production environment, you might restrict this
# to specific frontend origins for enhanced security.
CORS(app)

@app.route('/')
def hello():
    """
    A simple root route to confirm the Flask application is running.
    """
    logging.info("Root route accessed.")
    return "✅ Flask Article Extractor is Running!"

@app.route('/extract', methods=['POST'])
def extract_article():
    """
    Endpoint to extract article content from a given URL.
    Expects a JSON payload with a 'url' field.
    """
    try:
        data = request.get_json(force=True)
        logging.info(f"📥 Received data: {data}")

        url = data.get('url')
        if not url:
            logging.warning("❌ No URL provided in the request payload.")
            return jsonify({"error": "Missing URL"}), 400

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
        }
        
        # Fetch the content from the URL
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract all paragraph text to form the article content
        paragraphs = soup.find_all('p')
        article_text = ' '.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

        # Extract title, falling back to "No title" if not found
        title = soup.title.string.strip() if soup.title and soup.title.string else "No title"
        
        # Extract domain from the URL
        domain = urlparse(url).netloc.replace('www.', '')

        logging.info(f"✅ Extraction successful: Title='{title}', Domain='{domain}'")
        return jsonify({
            'title': title,
            'domain': domain,
            'url': url,
            'content': article_text
        })

    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Failed to fetch URL '{url}': {e}")
        return jsonify({"error": f"Failed to fetch URL: {e}"}), 500
    except Exception as e:
        logging.error(f"❌ An unexpected error occurred during extraction: {e}")
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

if __name__ == "__main__":
    # When running locally, Flask will use port 8080.
    # On Render, the $PORT environment variable will override this.
    app.run(host="0.0.0.0", port=8080)
