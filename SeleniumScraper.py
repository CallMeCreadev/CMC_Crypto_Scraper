import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
from CMC_new_tokens import CMC_new_tokens  # Import the CMC_new_tokens class


def init_driver(driver_path):
    print(driver_path)
    service = Service(executable_path=driver_path)
    return webdriver.Chrome(service=service)

class SeleniumScraper:
    def __init__(self, driver_path):
        # Initialize the WebDriver using the provided init_driver function
        self.driver = init_driver(driver_path)

    def open_page(self, url):
        self.driver.get(url)
        print(url)
        # Wait for the page to load completely
        time.sleep(5)

    def click_tab(self):
        # Find the tab using its unique attributes and click it
        tab = self.driver.find_element(By.XPATH, '//li[@data-index="tab-4"]')
        ActionChains(self.driver).move_to_element(tab).click(tab).perform()
        # Wait for the new content to load
        time.sleep(5)

    @staticmethod
    def convert_percent_to_number(percent_str):
        number_str = percent_str.replace('%', '').replace(',', '').strip()
        return float(number_str)

    def scrape_token_address(self):
        # Get the page source after clicking the tab
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        # Find the element containing the token address
        a_tag = soup.find('a', {'class': 'chain-name'})
        if a_tag:
            # Extract the value of the href attribute
            href = a_tag['href']
            # Extract the token address from the href
            token_address = href.split('/')[-1]
            return token_address
        else:
            print("Failed to find the token address element on the webpage.")
            return None

    def scrape_all_percent_change(self):
        # Get the page source after clicking the tab
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        # Find the new div containing the percentage change
        outer_div = soup.find('div', {'class': 'sc-65e7f566-0 gCtSWR'})
        if outer_div:
            main_div = outer_div.find('div', {'class': 'sc-4c05d6ef-0 sc-58c82cf9-0 dlQYLv dTczEt'})
            if main_div:
                # Look for the specific p tag within the main div
                percent_element = main_div.find('p', {'data-change': 'up'})
                if not percent_element:
                    percent_element = main_div.find('p', {'data-change': 'down'})

                if percent_element:
                    percent_text = percent_element.text.strip()
                    percent_value = percent_text.split('%')[0]
                    if percent_element.get('color') == 'red':
                        percent_value = '-' + percent_value
                    return percent_value + '%'
                else:
                    print("Failed to find the percent change element on the webpage.")
                    return None
            else:
                print("Failed to find the main div containing the percent change.")
                return None
        else:
            print("Failed to find the outer div containing the percent change.")
            return None

    def scrape_twitter_account(self):
        # Get the page source after clicking the tab
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        # Find all <a> tags with href attribute
        twitter_link = None
        for a_tag in soup.find_all('a', href=True):
            if 'twitter.com' in a_tag['href'] and 'Twitter' in a_tag.text:
                twitter_link = a_tag
                break

        if twitter_link:
            href = twitter_link['href']
            # Extract the Twitter handle from the href
            twitter_handle = href.split('/')[-1]
            return twitter_handle
        else:
            print("Failed to find the Twitter link on the webpage.")
            return None

    def extract_volume_change(self):
        # Get the page source after clicking the tab
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        # Find all the dd tags with the required class
        volume_elements = soup.find_all('dd', {'class': 'sc-65e7f566-0 dzgtSD base-text'})
        percent_element_count = 0

        for volume_element in volume_elements:
            # Look for the specific div within the dd tag
            main_div = volume_element.find('div', {'class': 'sc-4c05d6ef-0 sc-58c82cf9-0 dlQYLv dTczEt'})
            if main_div:
                # Look for all matching p tags within the main div
                percent_elements = main_div.find_all('p', {
                    'color': ['green', 'red'],
                    'data-change': ['up', 'down'],
                    'font-size': '1',
                    'class': 'sc-71024e3e-0 sc-58c82cf9-1 bgxfSG iPawMI'
                })

                for percent_element in percent_elements:
                    percent_element_count += 1
                    if percent_element_count == 2:  # Check if this is the second match
                        percent_text = percent_element.text.strip()
                        percent_value = float(percent_text.replace('%', ''))
                        if percent_element.get('color') == 'red':
                            percent_value = -percent_value
                        print("percent value: " + str(percent_value))
                        return percent_value

        # If no second matching element was found
        print("Failed to find the second percent element within the volume elements.")
        return None

    def close(self):
        self.driver.quit()

    def process_cmc_data(self, cmc_data):
        for row in cmc_data:
            url = row[10]
            if url:
                self.open_page(url)
                self.click_tab()
                address = self.scrape_token_address()
                percent_change = self.scrape_all_percent_change()
                twitter_account = self.scrape_twitter_account()
                print("twitter account " + str(twitter_account))
                volume_change = self.extract_volume_change()
                row.append(address)
                row.append(percent_change)
                row.append(twitter_account)
                row.append(volume_change)

    @staticmethod
    def clean_string(s):
        """
        Cleans up the input string by truncating at the first occurrence of '?'.

        Parameters:
        s (str): The input string to be cleaned.

        Returns:
        str: The cleaned string.
        """
        if '?' in s:
            return s.split('?')[0]
        return s

    def get_pruned_data(self):
        # Initialize CMC_new_tokens and get data
        cmc_new_tokens = CMC_new_tokens()
        data = cmc_new_tokens.get_data()

        # Process each row of data to scrape additional information
        self.process_cmc_data(data)

        pruned_data = []
        for row in data:
            print("row length " + str(len(row)))
            if len(row) < 15 or row[15] is None:
                continue
            if len(row) > 13 and CMC_new_tokens.convert_percent_to_number(row[5]) < -5 \
                    and CMC_new_tokens.convert_percent_to_number(row[13]) < -30 \
                    and CMC_new_tokens.convert_percent_to_number(row[4]) < 0:
                continue
            if len(row) > 13 and CMC_new_tokens.convert_percent_to_number(row[5]) < 0 \
                    and CMC_new_tokens.convert_percent_to_number(row[13]) < -50:
                continue
            if len(row) > 13 and row[11] < 0 \
                    and CMC_new_tokens.convert_percent_to_number(row[13]) < -50:
                continue
            if len(row) > 13 and CMC_new_tokens.convert_percent_to_number(row[5]) < 0 \
                    and row[15] < 0:
                continue
            # Apply clean_string to row[14]
            if len(row) > 14:
                row[14] = SeleniumScraper.clean_string(row[14])
            pruned_data.append(row)

        self.close()
        return pruned_data

    def save_pruned_data_to_file(self, filename):
        pruned_data = self.get_pruned_data()
        with open(filename, 'w') as f:
            json.dump(pruned_data, f)

# Usage example
if __name__ == "__main__":
    driver_path = "C:\\WebTools\\chromedriver.exe"  # Replace with the actual path to your WebDriver
    scraper = SeleniumScraper(driver_path)
    scraper.save_pruned_data_to_file("pruned_data.json")
