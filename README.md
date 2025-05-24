# Realtime India Metro News & Sentiment Analyzer 🇮🇳📊

Welcome to the Realtime India Metro News & Sentiment Analyzer! This project scrapes the latest news headlines for major Indian metropolitan cities (Bangalore, Mumbai, Delhi) from Google News RSS feeds, performs sentiment analysis using an AI model via OpenRouter, and presents the information through an interactive web dashboard featuring a 3D globe. An alternative Tkinter-based GUI is also available for local testing.

---
## ✨ Features

*   **Multi-City News Aggregation:** Fetches news for Bangalore, Mumbai, and Delhi.
*   **RSS Feed Parsing:** Utilizes Google News RSS feeds for up-to-date information.
*   **AI-Powered Sentiment Analysis:** Leverages LLMs via OpenRouter (specifically `nvidia/llama-3.1-nemotron-70b-instruct:free` as configured) to determine news sentiment.
*   **Interactive Web Dashboard:**
    *   Clean, responsive UI built with HTML, CSS, and JavaScript.
    *   3D Globe visualization (using Three.js & three-globe) to select and focus on cities.
    *   Near real-time updates of news and sentiment scores (via polling).
*   **Background Data Fetching:** The server continuously fetches and analyzes news in the background.
*   **Optional Desktop GUI:** A Tkinter-based interface (`test_ui.py`) for direct local news viewing and analysis (primarily for testing/development).
*   **Modular Design:** Separates concerns between news scraping/analysis logic (`news_scraper.py`) and the web server (`server.py`).

---
## 🛠️ Technology Stack

*   **Backend:**
    *   Python 3
    *   Flask (for the web server and API)
    *   Selenium (for browser automation, though primarily `requests` is used for current RSS feeds)
    *   `chromedriver-autoinstaller` (for easy ChromeDriver management)
    *   `requests` (for HTTP requests)
    *   `xml.etree.ElementTree` (for RSS parsing)
    *   `pytz` (for timezone handling)
    *   `openai` (Python client for interacting with OpenRouter API)
*   **Frontend:**
    *   HTML5
    *   CSS3 (with responsive design)
    *   JavaScript (ES6+)
    *   Three.js & three-globe (for 3D globe visualization)
    *   TWEEN.js (for smooth globe animations)
*   **APIs:**
    *   OpenRouter API (for sentiment analysis)
    *   Google News RSS Feeds

## ⚙️ Prerequisites

Before you begin, ensure you have the following installed:
*   Python (3.7 or higher recommended)
*   `pip` (Python package installer)
*   Git (for cloning the repository)
*   A modern web browser (e.g., Chrome, Firefox, Edge)
*   An active internet connection
---

## 🚀 Getting Started

Follow these steps to get the application up and running on your local machine:

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/mr-veyrion/Realtime_Sentiment_News_Analyzer.git
    cd Realtime_Sentiment_News_Analyzer
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    ```
    Activate the virtual environment:
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

3.  **Install Python Dependencies:**
    Make sure you have a `requirements.txt` file in the root of your project with the following content:
    Install the packages:
    ```bash
    pip install -r requirements.txt
    ```

4.  **ChromeDriver:**
    The `chromedriver-autoinstaller` package should automatically download and install the correct version of ChromeDriver when `news_scraper.py` is first run. If you encounter issues, ensure Google Chrome is installed.
    *Note: The script `news_scraper.py` contains `os.system('taskkill /im chromedriver.exe /f')` which is Windows-specific. If you are on macOS or Linux, you might need to remove or adapt this line if it causes issues.*

5.  **Configure API Key for Sentiment Analysis (Crucial!):**
    This application uses OpenRouter for sentiment analysis. You'll need an API key from them.
    *   Go to [OpenRouter.ai](https://openrouter.ai/) and sign up/log in to get your API key.
    *   Open the `news_scraper.py` file.
    *   Locate the `NewsScraperApp` class constructor (`__init__` method).
    *   Find the `self.client = OpenAI(...)` section.
    *   **Replace the placeholder API key with your actual OpenRouter API key:**
        ```python
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="YOUR_OPENROUTER_API_KEY_HERE", # <--- REPLACE THIS
            default_headers={
                "HTTP-Referer": "http://localhost:5000", # Or your actual app URL if deployed
                "X-Title": "News Analyzer" # Or your app's name
            }
        )
        ```
    *   **Important:** For production or shared repositories, it's highly recommended to use environment variables for API keys instead of hardcoding them.
---

## 🏃 Running the Application

You have two ways to run the application:

### 1. Web Dashboard (Recommended)

This will start the Flask web server and allow you to access the interactive dashboard in your browser.

```bash
python server.py
```

Once the server is running (it might take a few moments for the initial news fetch and Chrome initialization), open your web browser and navigate to:
➡️ http://localhost:5000

You should see the dashboard with the 3D globe and news cards for Bangalore, Mumbai, and Delhi.

### 2. Desktop GUI (Alternative for Testing)

This will launch the Tkinter-based desktop application.
```bash
python test_ui.py
```

This UI provides a more direct view of the news scraping and analysis, useful for development and testing.

---

## 🔧 Customization

This project is designed to be flexible. Here's how you can tailor it to your needs:

### 1. Adding or Changing News Locations (Cities, Regions, etc.)

You can monitor news from any location or topic that Google News can provide an RSS feed for.

**Steps to Get a Custom Google News RSS Feed URL:**

1.  **Open Google News:** Go to [news.google.com](https://news.google.com) in your web browser (Chrome is recommended for consistency with the search tools).
2.  **Perform an Advanced Search:**
    *   Look for the search bar. You might need to click the search icon (magnifying glass).
    *   Type a basic query for your desired location (e.g., "Pune").
    *   After the initial search results appear, look for a "Tools" button or filter options. If not immediately visible, you might find it under a "Search settings" or "Advanced search" link, or by appending specific parameters to the URL.
    *   **Alternatively, and more reliably for RSS, construct the search query directly:**
        Google News RSS feeds typically follow a pattern: `https://news.google.com/rss/search?q=YOUR_QUERY_HERE&hl=en-IN&gl=IN&ceid=IN:en`
        *   `q=YOUR_QUERY_HERE`: This is where your search terms go.
            *   For a specific city like "Pune": `q=Pune`
            *   For multiple keywords (e.g., "Pune" OR "Poona"): `q=Pune+OR+Poona`
            *   To get news from the last hour: `q=Pune+when:1h`
            *   To combine: `q=Pune+OR+Poona+when:1h`
        *   `hl=en-IN`: Language (English) and region (India). Adjust as needed (e.g., `hl=en-US` for US English).
        *   `gl=IN`: Geolocation bias (India). Adjust as needed (e.g., `gl=US`).
        *   `ceid=IN:en`: Confirms language and region.
3.  **Construct Your RSS URL:**
    *   Example for "Pune" news from the last hour:
        `https://news.google.com/rss/search?q=Pune+when:1h&hl=en-IN&gl=IN&ceid=IN:en`
    *   Example for "Chennai city development" from the last 2 hours:
        `https://news.google.com/rss/search?q=Chennai+city+development+when:2h&hl=en-IN&gl=IN&ceid=IN:en`
4.  **Test the RSS Feed:** Paste the constructed URL into your browser. You should see XML content (the RSS feed).
5.  **Update `news_scraper.py`:**
    *   Open the `news_scraper.py` file.
    *   Locate the `self.news_urls` dictionary within the `__init__` method of the `NewsScraperApp` class.
    *   Add or modify entries. The key is the display name for your location, and the value is the RSS feed URL you constructed.
        ```python
        self.news_urls = {
            'Bangalore': "https://news.google.com/rss/search?q=bangalore+OR+bengaluru+when:1h&hl=en-IN&gl=IN&ceid=IN:en",
            'Mumbai': "https://news.google.com/rss/search?q=mumbai+when:1h&hl=en-IN&gl=IN&ceid=IN:en",
            'Delhi': "https://news.google.com/rss/search?q=delhi+when:1h&hl=en-IN&gl=IN&ceid=IN:en",
            'Pune': "https://news.google.com/rss/search?q=Pune+when:1h&hl=en-IN&gl=IN&ceid=IN:en", # New city
            # Add more cities/locations here
        }
        ```
6.  **Update Frontend (if adding new cities):**
    *   If you add new cities that weren't in the original list (`Bangalore`, `Mumbai`, `Delhi`), you'll also need to update the `templates/index.html` file to include them in the city selector dropdown and create corresponding news card containers.
    *   Modify the loops:
        ```html
        <!-- In the city selector -->
        <select id="citySelector">
            <option value="all">All Cities</option>
            {% for city in cities %} <!-- 'cities' is passed from server.py -->
            <option value="{{ city|lower }}">{{ city }}</option>
            {% endfor %}
        </select>

        <!-- In the news grid -->
        {% for city in cities %} <!-- 'cities' is passed from server.py -->
        <div class="city-card" id="{{ city|lower }}-news">
            <h2>{{ city }} News <span class="sentiment-indicator"></span></h2>
            <div class="news-items" data-version="0"></div>
            <div class="analysis-result" data-version="0"></div>
        </div>
        {% endfor %}
        ```
    *   Ensure `server.py` passes the updated list of city names to the template. The `NewsScraperApp` instance in `server.py` will have the updated `news_urls.keys()`. You'll need to ensure these keys are passed to the `render_template` context:
        ```python
        # In server.py, inside the index route
        @app.route('/')
        def index():
            # Pass the city names from the scraper instance
            city_names = list(scraper.news_urls.keys())
            return render_template('index.html', cities=city_names)
        ```

### 2. Updating Globe Coordinates for New Locations

If you add new cities/locations, you'll want the globe to be able to focus on them.

1.  **Find Latitude and Longitude:**
    *   Use a service like Google Maps, Wikipedia, or an online geocoding tool to find the approximate latitude and longitude for your new location.
2.  **Update `static/js/globe.js`:**
    *   Open the `static/js/globe.js` file.
    *   Locate the `cityCoordinates` object:
        ```javascript
        const cityCoordinates = {
            'bangalore': [77.5946, 12.9716], // [longitude, latitude]
            'mumbai': [72.8777, 19.0760],
            'delhi': [77.1025, 28.7041]
        };
        ```
    *   Add a new entry for your location. The key should be the **lowercase version of the city name** used in your HTML `id` and dropdown `value` (e.g., 'pune'). The value is an array `[longitude, latitude]`.
        ```javascript
        const cityCoordinates = {
            'bangalore': [77.5946, 12.9716],
            'mumbai': [72.8777, 19.0760],
            'delhi': [77.1025, 28.7041],
            'pune': [73.8567, 18.5204] // Example for Pune
        };
        ```
    *   The `animateCameraTo(lng, lat)` function will then use these coordinates when the city is selected from the dropdown.

### 3. Sentiment Analysis Prompts

The prompts sent to the LLM for sentiment analysis are defined in the `send_to_analysis_api` and `analyze_news_trends` methods within `news_scraper.py`. You can tailor these:
*   To adjust the desired output format.
*   To focus on different aspects of the news (e.g., financial impact, social unrest).
*   To refine the sentiment scale or keywords.

### 4. LLM Model

The model used for sentiment analysis (currently `nvidia/llama-3.1-nemotron-70b-instruct:free`) is specified in `news_scraper.py` within the `self.client.chat.completions.create(...)` calls. You can change this to any other model supported by OpenRouter, keeping in mind:
*   **Compatibility:** Ensure the model is suitable for instruction-following or chat.
*   **Cost:** Different models have different pricing on OpenRouter.
*   **Capabilities:** Model performance on sentiment analysis tasks can vary.
*   **Rate Limits:** Be mindful of any rate limits associated with your chosen model or OpenRouter account.

### 5. Refresh Intervals

*   **Tkinter UI Auto-Refresh:** Controlled by `self.root.after(20000, self.auto_refresh)` in `news_scraper.py` (currently 20 seconds).
*   **Headless Mode Background Fetch:** Controlled by `time.sleep(20)` in the `run_headless` method in `news_scraper.py` (currently 20 seconds).
*   **Frontend Polling Interval:** Controlled by `setTimeout(updateNews, 1000)` in `static/js/news-updater.js` (currently 1 second). Adjust these values as needed, balancing freshness with API call frequency and server load.

---

## 💡 Troubleshooting

**API Key Errors:** If sentiment analysis isn't working, double-check your OpenRouter API key in news_scraper.py. Ensure it's active and has credits if required by the model.

### ChromeDriver Issues:

* Ensure Google Chrome is installed.
* If chromedriver-autoinstaller fails, you might need to manually install ChromeDriver and ensure its path is correctly configured or added to your system's PATH.
* The taskkill command in news_scraper.py is for Windows. If you're on macOS/Linux, you can remove it. If Chrome instances are not closing properly, you might need an equivalent command for your OS (e.g., pkill chromedriver).
* "Scraper not ready" or "Initializing..." on Web UI: Give the backend a minute or two to initialize, especially on the first run, as it needs to set up ChromeDriver and fetch initial news. Check the console output of server.py for any errors.
* Firewall/Network Issues: Ensure your firewall isn't blocking outgoing requests to Google News or OpenRouter.ai, or incoming connections to localhost:5000.

---

## 🤝 Contributing

Contributions are welcome! If you have suggestions, bug reports, or want to add new features, please feel free to:

* Fork the repository.
* Create a new branch (git checkout -b feature/YourAmazingFeature).
* Make your changes.
* Commit your changes (git commit -m 'Add some YourAmazingFeature').
* Push to the branch (git push origin feature/YourAmazingFeature).
* Open a Pull Request.
