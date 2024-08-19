import json
import requests
from bs4 import BeautifulSoup


class YesterdaysCoins:
    def __init__(self, filename):
        self.filename = filename
        self.data = self.load_data()
        self.urls = self.extract_urls()

    def load_data(self):
        with open(self.filename, 'r') as f:
            data = json.load(f)
        return data

    def extract_urls(self):
        urls = []
        for row in self.data:
            if "CMC" in row:
                urls.append(row["CMC"])
        return urls[:5]  # Only get the first 5 URLs

    def scrape_price(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            price_tag = soup.find('p', {'data-change': ['up', 'down']})
            if price_tag:
                price_text = price_tag.get_text().strip()
                color = price_tag.get('color')
                price = float(price_text.split('%')[0])
                if color == 'red':
                    price = -price
                return price
            else:
                print(f"Price not found on {url}")
                return None
        else:
            print(f"Failed to fetch {url}, status code: {response.status_code}")
            return None

    def compare_prices(self):
        prices = []
        for row in self.data[:5]:
            name = row.get("name", "")
            abbreviation = row.get("abbreviation", "")
            url = row.get("CMC", "")
            price = self.scrape_price(url)
            if price is not None:
                prices.append([name, abbreviation, url, price])
        return prices

    def save_prices_to_file(self, prices, filename):
        with open(filename, 'w') as f:
            json.dump(prices, f, indent=4)
        print(f"Prices saved to {filename}")

# Usage example
if __name__ == "__main__":
    input_filename = "yesterday_data.json"
    prices_output_filename = "yesterday_price_change.json"

    yesterdays_coins = YesterdaysCoins(input_filename)
    prices = yesterdays_coins.compare_prices()
    yesterdays_coins.save_prices_to_file(prices, prices_output_filename)
    print("Prices scraped and saved successfully.")
