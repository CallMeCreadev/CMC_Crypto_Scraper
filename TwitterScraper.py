import json
import random
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options


class GradeEnum:
    GRADE_MAPPING = {
        "A": 11,
        "A-": 10,
        "B+": 9,
        "B": 8,
        "B-": 7,
        "C+": 6,
        "C": 5,
        "C-": 4,
        "D+": 3,
        "D": 2,
        "D-": 1
    }

    @staticmethod
    def get_grade_value(grade):
        return GradeEnum.GRADE_MAPPING.get(grade, 0)  # Return 0 if grade is not found


def init_driver(driver_path):
    options = Options()
    # Optionally, set a user-agent directly without using fake-useragent
    # user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    # options.add_argument(f'user-agent={user_agent}')
    service = Service(executable_path=driver_path)
    return webdriver.Chrome(service=service, options=options)


class TwitterScraper:
    def __init__(self, driver_path):
        self.driver_path = driver_path
        self.driver = init_driver(driver_path)

    def open_page(self, url):
        self.driver.get(url)
        time.sleep(random.uniform(5, 13))  # Random sleep to mimic human behavior

    def scrape_socialblade_data(self, soup):
        def convert_k_to_number(value):
            if 'K' in value:
                return float(value.replace('K', '')) * 1000
            return float(value)

        last_30_day_followers = None
        last_30_day_tweets = None

        def extract_main_number(text):
            match = re.search(r'^\s*([\d\.K]+)', text)
            if match:
                return match.group(1)
            return None

        followers_elements = soup.find_all('p', style=lambda value: value and 'padding-left: 30px' in value)
        if followers_elements:
            followers_text = extract_main_number(followers_elements[0].text)
            if followers_text is None:
                return None, None
            last_30_day_followers = convert_k_to_number(followers_text)

        if len(followers_elements) > 1:
            tweets_text = extract_main_number(followers_elements[2].text)
            if tweets_text is None:
                return None, None
            last_30_day_tweets = convert_k_to_number(tweets_text)

        return last_30_day_followers, last_30_day_tweets

    def clean_grade_text(self, grade_text):
        # Use regex to keep only valid characters
        cleaned_grade = re.sub(r'[^A-DF+-]', '', grade_text)
        return cleaned_grade

    def scrape_grade(self, soup):
        grade_element = soup.find('div', style=lambda value: value and 'width: 122px' in value)
        if grade_element:
            grade_text = grade_element.text.strip()
            cleaned_grade_text = self.clean_grade_text(grade_text)
            grade_value = GradeEnum.get_grade_value(cleaned_grade_text)
            return grade_value
        else:
            print("Failed to find the grade element on the webpage.")
            return None

    def scrape_followers_increase(self, soup):
        followers_increase_element = soup.find('div', style=lambda value: value and 'width: 240px; height: 40px; line-height: 40px;' in value)
        if followers_increase_element:
            followers_increase_text = followers_increase_element.text.strip()
            match = re.search(r'\+(\d+)', followers_increase_text)
            if match:
                return int(match.group(1))
        print("Failed to find the followers increase element on the webpage.")
        return None

    def process_twitter_handles(self, pruned_data):
        twitter_data = []
        for row in pruned_data:
            if len(row) > 14:
                twitter_handle = row[14]
                self.open_page(f'https://socialblade.com/twitter/user/{twitter_handle}')
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                last_30_day_followers, last_30_day_tweets = self.scrape_socialblade_data(soup)
                if last_30_day_followers is None or last_30_day_tweets is None:
                    grade = None
                else:
                    grade = self.scrape_grade(soup)
                followers_increase = self.scrape_followers_increase(soup)
                row.append(last_30_day_followers)
                row.append(last_30_day_tweets)
                row.append(grade)
                row.append(followers_increase)
                twitter_data.append(row)
        return twitter_data

    def save_to_file(self, data, filename):
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    def close(self):
        self.driver.quit()

    def load_pruned_data_from_file(self, filename):
        with open(filename, 'r') as f:
            pruned_data = json.load(f)
        return pruned_data

    def filter_twitter_data(self, twitter_data):
        filtered_data = [
            row for row in twitter_data
            if row[16] not in (None, 1, 2, 3)
        ]
        return filtered_data


# Usage example
if __name__ == "__main__":
    driver_path = "C:\\WebTools\\chromedriver.exe"  # Replace with the actual path to your WebDriver

    twitter_scraper = TwitterScraper(driver_path)
    pruned_data = twitter_scraper.load_pruned_data_from_file("pruned_data.json")
    twitter_data = twitter_scraper.process_twitter_handles(pruned_data)
    filtered_twitter_data = twitter_scraper.filter_twitter_data(twitter_data)

    # Save filtered data to 'filtered_twitter_data.json'
    twitter_scraper.save_to_file(filtered_twitter_data, "filtered_twitter_data.json")

    twitter_scraper.close()

    for row in filtered_twitter_data:
        print(row)
