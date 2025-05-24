import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logging

from flask import Flask, render_template, jsonify, Response
from news_scraper import NewsScraperApp
import threading
import time
import json

app = Flask(__name__)
scraper = NewsScraperApp()  # No UI (root is None)

# Start the headless news-fetching process in a separate thread
threading.Thread(target=scraper.run_headless, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html', cities=['Bangalore', 'Mumbai', 'Delhi'])

@app.route('/news-data')
def news_data():
    try:
        if not scraper or not scraper.ready.wait(timeout=10):
            return jsonify({'error': 'Initializing...'}), 202
            
        response_data = []
        for city in scraper.news_urls.keys():
            items = scraper.get_news_items(city)
            analysis = scraper.analyze_news_trends(city) if items else "No news available"
            response_data.append({
                'name': city.lower(),  # Match frontend ID format
                'items': items,
                'analysis': analysis,
                'updated': time.time()
            })
            
        return jsonify({'news': response_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status')
def status():
    return jsonify({
        'scraper_ready': scraper.ready.is_set() if scraper else False,
        'chrome_initialized': scraper.driver is not None if scraper else False
    })

@app.route('/news-stream')
def news_stream():
    def event_stream():
        while True:
            try:
                if not scraper or not scraper.ready.wait(timeout=10):
                    yield 'data: {"error": "Scraper initialization timed out"}\n\n'
                    continue
                
                news_data = {
                    'news': [{
                        'name': city,
                        'items': scraper.get_news_items(city),
                        'analysis': scraper.analyze_news_trends(city)
                    } for city in scraper.news_urls.keys()]
                }
                yield f'data: {json.dumps(news_data)}\n\n'
                time.sleep(2)  # Check for updates every 2 seconds
            except Exception as e:
                yield f'data: {{"error": "{str(e)}"}}\n\n'
                time.sleep(5)

    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False) 