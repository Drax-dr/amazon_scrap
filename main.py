import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0',
    "Accept-Language": "en-US,en;q=0.5"
}

def get_text(soup, selector, default='N/A'):
    tag = soup.select_one(selector)
    return tag.get_text(strip=True) if tag else default

def get_table_value(soup, label):
    tag = soup.find('th', string=label)
    return tag.find_next('td').get_text(strip=True) if tag else 'N/A'

def scrape_product_details(url):
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Failed to fetch {url}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        return {
            'Product URL': url,
            'Product Name': get_text(soup, 'span.a-size-medium'),
            'Product Price': get_text(soup, 'span.a-price-whole'),
            'Rating': get_text(soup, 'span.a-icon-alt'),
            'Number of Reviews': get_text(soup, '#acrCustomerReviewText'),
            'ASIN': get_table_value(soup, 'ASIN'),
            'Manufacturer': get_table_value(soup, 'Manufacturer'),
            'Product Description': get_text(soup, '#productDescription')
        }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def scrape_search_results(product, num_pages):
    all_data = []
    for page in range(1, num_pages + 1):
        search_url = f'https://www.amazon.in/s?k={product}&page={page}'
        try:
            response = requests.get(search_url, headers=HEADERS)
            if response.status_code != 200:
                print(f"Failed to fetch search page {page}")
                continue

            soup = BeautifulSoup(response.content, 'html.parser')
            product_links = [a['href'] for a in soup.select('.s-main-slot a.s-no-outline')]

            for link in product_links:
                full_url = f"https://www.amazon.in{link}"
                product_data = scrape_product_details(full_url)
                if product_data:
                    all_data.append(product_data)
                time.sleep(1.5)  # Polite delay to avoid blocking
        except Exception as e:
            print(f"Error on search page {page}: {e}")
    return all_data

if __name__ == "__main__":
    product = input("Enter a product: ")
    pages = int(input("Enter no of pages: "))
    result_data = scrape_search_results(product, num_pages=pages)

    if result_data:
        df = pd.DataFrame(result_data)
        df.to_csv("amazon_product_data.csv", index=False)
        print("Data saved to amazon_product_data.csv")
    else:
        print("No data was scraped.")
