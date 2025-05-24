import tkinter as tk
from news_scraper import NewsScraperApp

def main():
    root = tk.Tk()
    root.title("News & Sentiment Analysis Test UI")
    root.geometry("1500x800")
    app = NewsScraperApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 