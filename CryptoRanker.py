import json

class CryptoRanker:
    def __init__(self, filename):
        self.filename = filename
        self.data = self.load_data()

    def load_data(self):
        with open(self.filename, 'r') as f:
            data = json.load(f)
        return data

    def rank_data(self):
        # Define the indices of the values we want to rank
        rank_indices = {
            'desc': [5, 15, 16, 17],  # Indices of values to rank in descending order (excluding 18)
            'asc': [11]                    # Indices of values to rank in ascending order
        }

        # Create a ranking for each index
        for rank_type, indices in rank_indices.items():
            for index in indices:
                self.rank_column(index, ascending=(rank_type == 'asc'))

        # Sum the ranks to create a score, subtracting row[18] from the score
        for row in self.data:
            rank_score = sum(row[-5:]) - self.convert_value(row[18])
            row.append(rank_score)

        # Sort the data by the calculated rank (now at row[25] instead of row[26] due to the change)
        self.data.sort(key=lambda x: x[-1])

    def convert_value(self, value):
        if isinstance(value, str) and '%' in value:
            return float(value.replace('%', '').strip())
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0  # Return 0.0 if the value is not convertible to float

    def rank_column(self, index, ascending=True):
        sorted_data = sorted(self.data, key=lambda x: self.convert_value(x[index]), reverse=not ascending)
        for rank, row in enumerate(sorted_data, start=1):
            row.append(rank)
            print(f"Index {index}, Rank {rank}, Value {row[index]}")  # Debug print

    def save_ranked_data(self, output_filename):
        with open(output_filename, 'w') as f:
            json.dump(self.data, f, indent=4)

# Usage example
if __name__ == "__main__":
    input_filename = "filtered_twitter_data.json"
    output_filename = "ranked_crypto_data.json"

    crypto_ranker = CryptoRanker(input_filename)
    crypto_ranker.rank_data()
    crypto_ranker.save_ranked_data(output_filename)

    for row in crypto_ranker.data:
        print(row)
