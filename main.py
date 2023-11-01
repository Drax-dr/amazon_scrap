import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_product_details(url):
    headers = {'User-Agent': 'Mozilla 5.0',"Accept-Language": "en-US,en;q=0.5"}
    response = requests.get(url, headers=headers)
    print(response)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract product details
        product_name = soup.find('span', {'class': 'a-size-medium'}).get_text(strip=True)
        product_price = soup.find('span', {'class': 'a-price-whole'}).get_text(strip=True)
        rating = soup.find('span', {'class': 'a-icon-alt'}).get_text(strip=True)
        num_reviews = soup.find('span', {'id': 'acrCustomerReviewText'}).get_text(strip=True)
        asin = soup.find('th', text='ASIN').find_next('td').get_text(strip=True)
        product_description = soup.find('span', {'id': 'productDescription'}).get_text(strip=True)
        manufacturer = soup.find('th', text='Manufacturer').find_next('td').get_text(strip=True)

        return {
            'Product URL': url,
            'Product Name': product_name,
            'Product Price': product_price,
            'Rating': rating,
            'Number of Reviews': num_reviews,
            'ASIN': asin,
            'Product Description': product_description,
            'Manufacturer': manufacturer
        }
    else:
        print(f"Failed to fetch data from URL: {url}")
        return None

data = []

num_pages = 20

for page in range(1, num_pages + 1):
    page_url = f'https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_{page}'
    headers = {'User-Agent': 'Mozilla 5.0',"Accept-Language": "en-US,en;q=0.5"}
    response = requests.get(page_url, headers=headers)
    print(response)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        product_links = [a['href'] for a in soup.select('.s-main-slot a.s-no-outline')]
        # print(product_links)
        for link in product_links:
            
            product_url = f'https://www.amazon.in{link}'
            product_data = scrape_product_details(product_url)
            if product_data:
                data.append(product_data)

print(data)

df = pd.DataFrame(data)

print(df)

df.to_csv('amazon_product_data.csv', index=False)
