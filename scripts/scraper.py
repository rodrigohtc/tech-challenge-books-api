import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import time

BASE = "https://books.toscrape.com/"
CATALOGUE = urljoin(BASE, "catalogue/")

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})
retries = Retry(total=3, backoff_factor=0.3, status_forcelist=[429, 500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))
session.mount("http://", HTTPAdapter(max_retries=retries))

def get_soup(url: str) -> BeautifulSoup:
    try:
        r = session.get(url, timeout=30)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except requests.exceptions.SSLError:
        # fallback p/ http se houver problema de certificado
        url_http = url.replace("https://", "http://", 1)
        r = session.get(url_http, timeout=30, verify=False)  # apenas para este site de exemplo
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")

def extract_categories() -> dict:
    soup = get_soup(BASE)
    cats = {}
    for a in soup.select("div.side_categories ul li ul li a"):
        name = a.text.strip()
        href = urljoin(BASE, a["href"])
        cats[name] = href
    return cats

def extract_books_from_category(cat_name: str, cat_url: str):
    books = []
    page_url = cat_url
    while True:
        soup = get_soup(page_url)
        for pod in soup.select(".product_pod"):
            title = pod.h3.a["title"].strip()
            price_text = pod.select_one(".price_color").text.strip().lstrip("£").replace(",", ".")
            rating = pod.p["class"][1]  # e.g., 'One', 'Two'
            availability = pod.select_one(".instock.availability").text.strip()
            rel_link = pod.h3.a["href"]
            # some product links are relative with ../
            product_link = urljoin(CATALOGUE, rel_link.replace("../../../", ""))
            img = urljoin(BASE, pod.img["src"].lstrip("./"))
            books.append({
                "title": title,
                "price": price_text,
                "rating": rating,
                "availability": availability,
                "category": cat_name,
                "link": product_link,
                "image": img,
            })
        # next page?
        next_li = soup.select_one("li.next a")
        if next_li and next_li.get("href"):
            page_url = urljoin(page_url, next_li["href"])
            time.sleep(0.3)
        else:
            break
    return books

def run():
    all_books = []
    cats = extract_categories()
    for name, url in cats.items():
        print(f"Scraping category: {name}")
        all_books.extend(extract_books_from_category(name, url))
    df = pd.DataFrame(all_books)
    df = df.reset_index().rename(columns={"index": "id"})
    df.to_csv("data/books.csv", index=False)
    print(f"Saved {len(df)} books to data/books.csv")

if __name__ == "__main__":
    run()
