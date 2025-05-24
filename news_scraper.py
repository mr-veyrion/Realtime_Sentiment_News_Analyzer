import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller
import os
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
import pytz
from openai import OpenAI
from requests.utils import requote_uri

class NewsScraperApp:
    def __init__(self, root=None):
        self.root = root
        self.ready = threading.Event()  # Thread-safe ready flag
        self.driver = None
        
        # Start Chrome setup immediately
        self.chrome_thread = threading.Thread(target=self.initialize_chrome)
        self.chrome_thread.start()
        
        if self.root:  # Only setup GUI if root exists
            self.root.title("India Metro News Hub")
            self.root.geometry("1500x800")
            self.create_ui()
            # Schedule auto-refresh only in GUI mode
            self.root.after(20000, self.auto_refresh)
        
        # Updated URLs to use RSS feeds
        self.news_urls = {
            'Bangalore': "https://news.google.com/rss/search?q=bangalore+OR+bengaluru+when:1h&hl=en-IN&gl=IN&ceid=IN:en",
            'Mumbai': "https://news.google.com/rss/search?q=mumbai+when:1h&hl=en-IN&gl=IN&ceid=IN:en",
            'Delhi': "https://news.google.com/rss/search?q=delhi+when:1h&hl=en-IN&gl=IN&ceid=IN:en"
        }
        
        # Initialize OpenAI client
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="YOUR API",   # Mention your API KEY
            default_headers={
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "News Analyzer"
            }
        )
        
        # Initialize news cache BEFORE fetching news
        self.news_cache = {}
        # Create a lock for synchronizing cache access
        self.cache_lock = threading.Lock()
        
        # Start initial fetch now that the cache is ready
        self.fetch_all_cities()
        
    def initialize_chrome(self):
        """Initialize Chrome in a separate thread"""
        try:
            print("Starting Chrome initialization...")
            options = Options()
            options.add_argument('--headless=new')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--remote-debugging-port=0')  # Use random port instead of 9222
            
            # Clear any existing ChromeDriver processes
            os.system('taskkill /im chromedriver.exe /f')
            
            # Explicit path handling with version check
            chromedriver_path = chromedriver_autoinstaller.install()
            print(f"Using ChromeDriver at: {chromedriver_path}")
            
            service = Service(
                executable_path=chromedriver_path,
                service_args=['--verbose', '--log-path=chromedriver.log']
            )
            
            # Add retry logic for initialization
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    self.driver = webdriver.Chrome(service=service, options=options)
                    self.driver.get('https://google.com')
                    print("Chrome test navigation successful")
                    self.ready.set()
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"Retrying Chrome initialization ({attempt+1}/{max_retries})...")
                        time.sleep(2)
                    else:
                        raise e
                        
        except Exception as e:
            print(f"Chrome initialization FAILED: {str(e)}")
            self.ready.clear()
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
            # Fallback to direct requests if Chrome fails
            print("Falling back to pure requests-based scraping")
            self.driver = None
            self.ready.set()
        
    def create_ui(self):
        """Create the user interface"""
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Style configuration
        style = ttk.Style()
        style.configure("City.TLabel", 
                       font=("Helvetica", 16, "bold"),
                       background="#2c3e50",
                       foreground="#ffffff",
                       padding=10)
        
        # Create news and analysis sections
        self.news_areas = {}
        self.analysis_areas = {}
        self.status_labels = {}
        
        for i, city in enumerate(['Bangalore', 'Mumbai', 'Delhi']):
            # Main city container
            city_frame = ttk.Frame(self.main_frame)
            city_frame.grid(row=0, column=i, padx=10, sticky="nsew")
            
            self.main_frame.columnconfigure(i, weight=1)
            
            # City header
            city_label = ttk.Label(
                city_frame,
                text=f"{city} News",
                style="City.TLabel"
            )
            city_label.pack(fill=tk.X, pady=(0, 10))
            
            # News area
            news_area = scrolledtext.ScrolledText(
                city_frame,
                wrap=tk.WORD,
                font=("Arial", 10),
                height=15,
                background="#ffffff",
                padx=10,
                pady=10
            )
            news_area.pack(fill=tk.BOTH, expand=True)
            self.news_areas[city] = news_area
            
            # Status label
            status_label = ttk.Label(city_frame, text="Ready")
            status_label.pack(pady=5)
            self.status_labels[city] = status_label
            
            # Analysis section
            analysis_label = ttk.Label(
                city_frame,
                text="Sentiment Analysis",
                style="City.TLabel"
            )
            analysis_label.pack(fill=tk.X, pady=(10, 5))
            
            analysis_area = scrolledtext.ScrolledText(
                city_frame,
                wrap=tk.WORD,
                font=("Arial", 10),
                height=10,
                background="#f8f8f8",
                padx=10,
                pady=10
            )
            analysis_area.pack(fill=tk.BOTH, expand=True)
            self.analysis_areas[city] = analysis_area
        
        # Refresh button
        self.refresh_btn = ttk.Button(
            self.main_frame,
            text="🔄 Refresh All",
            command=self.fetch_all_cities
        )
        self.refresh_btn.grid(row=1, column=0, columnspan=3, pady=10)
        
    def fetch_news_for_city(self, city):
        # If a GUI exists, update its UI elements.
        if self.root is not None:
            self.news_areas[city].delete(1.0, tk.END)
            self.analysis_areas[city].delete(1.0, tk.END)
            self.status_labels[city].config(text="Fetching news...")
        else:
            print(f"Fetching news for {city} in headless mode...")

        try:
            print(f"\nFetching news for {city}...")
            headers = {'User-Agent': 'Mozilla/5.0'}  # Add a User-Agent header
            url = requote_uri(self.news_urls[city])
            print(f"Using URL for {city}: {url}")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            root_element = ET.fromstring(response.content)

            items = root_element.findall('.//item')
            print(f"Found {len(items)} news items for {city}")

            news_items = []
            for item in items:
                try:
                    title = item.find('title').text
                    link = item.find('link').text
                    pubDate = item.find('pubDate').text
                    source = item.find('source').text if item.find('source') is not None else "Unknown Source"

                    try:
                        pub_datetime = datetime.strptime(pubDate, '%a, %d %b %Y %H:%M:%S %Z')
                    except ValueError:
                        pub_datetime = datetime.now()

                    pub_datetime = pub_datetime.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone('Asia/Kolkata'))
                    timestamp = pub_datetime.strftime('%I:%M %p')

                    news_items.append({
                        'headline': title.strip(),
                        'source': source.strip(),
                        'subheading': f"Published at {timestamp}",
                        'timestamp': timestamp,
                        'link': link.strip()
                    })
                    print(f"Processed: {title[:50]}...")
                except Exception as e:
                    print(f"Error processing item: {e}")
                    continue

            # UI update:
            if self.root is not None:
                if news_items and self.root.winfo_exists():
                    self.update_city_news(city, news_items)
                else:
                    self.status_labels[city].config(text="No recent news found")
            else:
                print(f"{city} News fetched: {len(news_items)} items")

            if news_items:
                self.send_to_analysis_api(city, news_items)
            else:
                print(f"No news items processed for {city}, skipping API analysis.")

            print(f"Fetched {len(news_items)} items for {city}")
            self.news_cache[city] = news_items

        except Exception as e:
            print(f"SCRAPER ERROR ({city}): {e}")
            self.news_cache[city] = []
        
    def update_city_news(self, city, news_items):
        """Update the news display for a city"""
        with self.cache_lock:
            self.news_cache[city] = news_items
        
        try:
            news_area = self.news_areas[city]
            news_area.delete(1.0, tk.END)
            
            print(f"Updating display for {city} with {len(news_items)} items")
            
            for i, news in enumerate(news_items, 1):
                # Add headline
                news_area.insert(tk.END, f"{i}. ", "number")
                news_area.insert(tk.END, f"{news['headline']}\n", "headline")
                
                # Add source
                news_area.insert(tk.END, f"Source: {news['source']}\n", "source")
                
                # Add description
                news_area.insert(tk.END, f"{news['subheading']}\n", "subheading")
                
                # Add timestamp
                news_area.insert(tk.END, f"Posted: {news['timestamp']}\n", "timestamp")
                
                news_area.insert(tk.END, "─" * 50 + "\n\n", "separator")
            
            # Configure tags
            news_area.tag_configure("number", font=("Arial", 10, "bold"), foreground="#666666")
            news_area.tag_configure("headline", font=("Arial", 11, "bold"))
            news_area.tag_configure("source", font=("Arial", 9), foreground="#666666")
            news_area.tag_configure("subheading", font=("Arial", 10))
            news_area.tag_configure("timestamp", font=("Arial", 9, "italic"), foreground="#0066cc")
            news_area.tag_configure("separator", foreground="#cccccc")
            
            self.status_labels[city].config(text=f"Found {len(news_items)} news items")
            print(f"Display updated for {city}")
            
        except Exception as e:
            print(f"Error updating display: {str(e)}")
        
    def fetch_all_cities(self):
        """Fetch news for all cities"""
        # Disable the refresh button if running in GUI mode.
        if self.root:
            self.refresh_btn.config(state='disabled')
        
        def fetch_task():
            # Fetch news for each city sequentially.
            for city in self.news_urls.keys():
                # (Optional) Check if the window is still alive.
                if self.root and not self.root.winfo_exists():
                    break
                self.fetch_news_for_city(city)
            
            # Re-enable the refresh button on the main thread.
            if self.root and self.root.winfo_exists():
                self.root.after(0, lambda: self.refresh_btn.config(state='normal'))
        
        # Run the fetching task in a separate thread.
        t = threading.Thread(target=fetch_task, daemon=True)
        t.start()
        
    def auto_refresh(self):
        """Auto refresh news every 20 seconds"""
        self.fetch_all_cities()
        self.root.after(20000, self.auto_refresh)
        
    def send_to_analysis_api(self, city, news_items):
        """Send complete news data to analysis API with custom instructions"""
        try:
            headlines = "\n".join([item['headline'] for item in news_items])
            
            # Custom API instructions
            analysis_prompt = f"""Analyze sentiment and key themes of these {city} news headlines. Follow these rules:
1. Start with overall sentiment (Very Negative/Negative/Neutral/Positive/Very Positive)
2. Read and analyse the headlines and get a detailed analysis of the news.
3. Highlight any urgent or developing situations
4. Use bullet points for clarity
5. Just give the analysis in the response, of numbers(Very Negative/Negative/Neutral/Positive/Very Positive)

Example response 1:
Sentiment: Positive
Your Output: 4

Example response 2:
Sentiment: Negative
Your Output: 2

Example response 3:
Sentiment: Neutral
Your Output: 3

Example response 4:
Sentiment: Very Negative
Your Output: 1

Example response 5:
Sentiment: VeryPositive
Your Output: 5

You are not suppose to give any other text in the response, just the numbers.
Headlines to analyze: {headlines}"""
            
            response = self.client.chat.completions.create(
                model="nvidia/llama-3.1-nemotron-70b-instruct:free",
                messages=[{
                    "role": "user",
                    "content": analysis_prompt
                }]
            )
            analysis = response.choices[0].message.content
            
            if self.root and self.root.winfo_exists():
                self.analysis_areas[city].delete(1.0, tk.END)
                self.analysis_areas[city].insert(tk.END, analysis)
            
        except Exception as e:
            print(f"API Error for {city}: {str(e)}")
            if self.root and self.root.winfo_exists():
                self.analysis_areas[city].insert(tk.END, f"Analysis error: {str(e)}")

    def store_analysis(self, city, analysis):
        """Update the analysis display"""
        def update_display():
            self.analysis_areas[city].config(state=tk.NORMAL)
            self.analysis_areas[city].delete(1.0, tk.END)
            self.analysis_areas[city].insert(tk.END, analysis)
            self.analysis_areas[city].config(state=tk.DISABLED)
            
        if self.root.winfo_exists():
            self.root.after(0, update_display)
        
        print(f"\nAnalysis for {city}:")
        print(analysis)

    def get_news_items(self, city):
        """Thread-safe news cache access"""
        with self.cache_lock:  # Add this lock initialization in __init__
            return self.news_cache.get(city, []).copy()  # Return a copy
        
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()

    def run_headless(self):
        """Headless mode operation"""
        self.ready.wait()  # Wait for Chrome initialization

        # Perform an immediate synchronous fetch for all cities before entering the refresh loop.
        for city in self.news_urls.keys():
            self.fetch_news_for_city(city)

        while True:
            self.fetch_all_cities()
            time.sleep(20)

    def analyze_news_trends(self, city):
        """Identify long-term trends with custom instructions"""
        try:
            news_text = "\n".join([item['headline'] for item in self.news_cache.get(city, [])])
            if not news_text:
                return "No news available for trend analysis"
            
            # Trend analysis specific instructions
            trend_prompt = f"""Analyze sentiment of these {city} news headlines. Rules:
1. Return ONLY one of these numbers based on overall sentiment:
   - 1: Very Negative
   - 2: Negative 
   - 3: Neutral
   - 4: Positive
   - 5: Very Positive
2. Base your analysis strictly on the headlines below
3. No additional text or formatting only numbers

Headlines:
{news_text}"""
            
            response = self.client.chat.completions.create(
                model="nvidia/llama-3.1-nemotron-70b-instruct:free",
                messages=[{
                    "role": "user",
                    "content": trend_prompt
                }]
            )
            return self._convert_sentiment_number(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Trend analysis failed for {city}: {str(e)}")
            return "3"  # Fallback to neutral

    def _convert_sentiment_number(self, response):
        """Convert numeric response to text label"""
        try:
            num = int(response.strip())
            if 1 <= num <= 5:
                return ["Very Negative", "Negative", "Neutral", "Positive", "Very Positive"][num-1]
            return "Neutral"
        except:
            return "Neutral"

    def parse_rss_feed(self, rss_content):
        """Parse RSS XML content"""
        try:
            root = ET.fromstring(rss_content)
            items = []
            for item in root.findall('.//item'):
                try:
                    items.append({
                        'headline': item.find('title').text.strip(),
                        'link': item.find('link').text.strip(),
                        'source': item.find('source').text.strip() if item.find('source') is not None else 'Unknown',
                        'timestamp': datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S %Z')
                    })
                except AttributeError as e:
                    print(f"RSS item parse error: {str(e)}")
                    continue
            return items
        except ET.ParseError as e:
            print(f"Invalid RSS XML: {str(e)}")
            return []

if __name__ == "__main__":
    root = tk.Tk()
    app = NewsScraperApp(root)
    root.mainloop()
