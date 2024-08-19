import requests
from bs4 import BeautifulSoup

class CMC_new_tokens:
    def __init__(self):
        self.url = 'https://coinmarketcap.com/new/'
        self.headers = []
        self.data = []

    @staticmethod
    def convert_dollar_to_number(dollar_str):
        number_str = dollar_str.replace('$', '').replace(',', '')
        number = float(number_str)
        return number

    @staticmethod
    def divide_dollar_values(first_dollar_str, second_dollar_str):
        first_number = CMC_new_tokens.convert_dollar_to_number(first_dollar_str)
        second_number = CMC_new_tokens.convert_dollar_to_number(second_dollar_str)
        if second_number == 0:
            return None  # Handle division by zero
        result = first_number / second_number
        return result

    @staticmethod
    def is_positive(value_str):
        number_str = value_str.replace('$', '').replace(',', '').replace('%', '').replace('icon-Caret-up', '').replace('icon-Caret-down', '').strip()
        number = float(number_str)
        return number > 0

    @staticmethod
    def extract_and_format_name(cell1, cell2):
        cell1_str = str(cell1)
        cell2_str = str(cell2)
        pos = cell2_str.find(cell1_str)
        if pos != -1:
            name_part = cell2_str[:pos].strip()
            name_part = name_part.replace(' ', '-')
            return name_part
        return ""

    @staticmethod
    def parse_cell_value(cell_value):
        cell_value_str = cell_value.replace('$', '').replace(',', '').replace('%', '').replace('icon-Caret-up', '').replace('icon-Caret-down', '').strip()
        return float(cell_value_str)

    @staticmethod
    def extract_href(cell):
        a_tag = cell.find('a', {'class': 'cmc-link'})
        if a_tag and 'href' in a_tag.attrs:
            return 'https://coinmarketcap.com' + a_tag['href']
        return None

    @staticmethod
    def convert_percent_to_number(percent_str):
        number_str = percent_str.replace('%', '').replace(',', '').strip()
        return float(number_str)

    def get_data(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table', {'class': 'cmc-table'})
            self.headers = [header.text for header in table.find_all('th')]
            rows = table.find('tbody').find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                cell_data = []
                skip_row = False
                for i, cell in enumerate(cells):
                    icon_caret_down = cell.find('span', {'class': 'icon-Caret-down'})
                    icon_caret_up = cell.find('span', {'class': 'icon-Caret-up'})
                    cell_text = cell.text.strip()
                    if icon_caret_down:
                        cell_text = "-" + cell_text.replace('icon-Caret-down', '').strip()
                    elif icon_caret_up:
                        cell_text = cell_text.replace('icon-Caret-up', '').strip()
                    if i in [5, 6] and cell_text == "--":
                        skip_row = True
                        break
                    cell_data.append(cell_text)
                if not skip_row:
                    href = self.extract_href(cells[2])
                    cell_data.append(href)
                    self.data.append(cell_data)
            for i, row in enumerate(self.data):
                if len(row) > 7:
                    first_dollar_str = row[6]
                    second_dollar_str = row[7]
                    try:
                        ratio = self.divide_dollar_values(first_dollar_str, second_dollar_str)
                    except ValueError:
                        ratio = None
                    row.append(ratio)
            self.headers.append("Ratio")
            self.headers.append("Href")
            filtered_data = [
                row for row in self.data
                if all(cell is not None for cell in row) and
                self.parse_cell_value(row[4]) >= -30 and
                self.parse_cell_value(row[5]) >= -30 and
                (row[11] is None or row[11] <= 25) and
                self.parse_cell_value(row[7]) >= 100000 and
                row[8] in ['Ethereum', 'BNB', 'Solana']
            ]
            filtered_data.sort(
                key=lambda x: (x[11] if x[11] is not None else float('inf'), CMC_new_tokens.convert_percent_to_number(x[5]) < 0))
            self.data = filtered_data
        else:
            print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return self.data

# Example usage
if __name__ == "__main__":
    cmc_new_tokens = CMC_new_tokens()
    data = cmc_new_tokens.get_data()
    for row in data:
        print(row)
