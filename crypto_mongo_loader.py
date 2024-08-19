import json
import pymongo
import re
import math
from datetime import datetime, timedelta
from bson import ObjectId  # Import ObjectId from bson

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        elif isinstance(o, ObjectId):  # Handle ObjectId
            return str(o)
        return super().default(o)

class CryptoMongoLoader:
    def __init__(self, today_filename, yesterday_prices_filename, mongo_uri, db_name, today_collection_name, yesterday_collection_name):
        self.today_filename = today_filename
        self.yesterday_prices_filename = yesterday_prices_filename
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.today_collection_name = today_collection_name
        self.yesterday_collection_name = yesterday_collection_name
        self.today_data = self.load_data(self.today_filename)
        self.yesterday_data = self.load_data(self.yesterday_prices_filename)

    def load_data(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        return data

    def process_today_data(self):
        mongo_data = []
        for row in self.today_data[:5]:  # Only process the first 5 rows
            processed_row = {}
            name_abbr = re.split(r'\s*' + re.escape(row[1]) + r'\s*', row[2])
            processed_row["name"] = name_abbr[0] if len(name_abbr) > 0 else ""
            processed_row["abbreviation"] = name_abbr[1] if len(name_abbr) > 1 else ""
            processed_row["market_cap"] = row[6]
            processed_row["volume_24h"] = row[7]
            processed_row["volume_24h_change"] = f"{row[15]}%"
            processed_row["price_change_24h"] = row[5]
            processed_row["price_change_all_time"] = row[13]
            processed_row["30d_twitter_followers"] = round(float(row[16]))
            processed_row["30d_tweets"] = round(float(row[17]))
            processed_row["CMC"] = row[10]
            processed_row["chain"] = row[8]
            processed_row["address"] = row[12]
            processed_row["type"] = "TodaysCoins"
            processed_row["timestamp"] = datetime.utcnow().isoformat()  # Convert to ISO format string

            mongo_data.append(processed_row)
            print(processed_row)

        return mongo_data

    def process_yesterday_data(self):
        mongo_data = []
        for row in self.yesterday_data:
            processed_row = {
                "name": row[0],
                "abbreviation": row[1],
                "CMC": row[2],
                "price_change": f"{row[3]}%",
                "type": "YesterdaysCoins",
                "timestamp": datetime.utcnow().isoformat()  # Convert to ISO format string
            }
            mongo_data.append(processed_row)
            print(processed_row)

        return mongo_data

    def load_to_mongo(self, today_data, yesterday_data):
        client = pymongo.MongoClient(self.mongo_uri)
        db = client[self.db_name]
        today_collection = db[self.today_collection_name]
        yesterday_collection = db[self.yesterday_collection_name]

        # Delete records older than 2 months from today's collection
        two_months_ago = datetime.utcnow() - timedelta(days=60)
        two_months_ago_iso = two_months_ago.isoformat()
        result_today = today_collection.delete_many({"timestamp": {"$lt": two_months_ago_iso}})
        print(f"Deleted {result_today.deleted_count} records older than 2 months from today's collection.")

        # Delete records older than 2 months from yesterday's collection
        result_yesterday = yesterday_collection.delete_many({"timestamp": {"$lt": two_months_ago_iso}})
        print(f"Deleted {result_yesterday.deleted_count} records older than 2 months from yesterday's collection.")

        # Insert new data into today's collection
        today_collection.insert_many(today_data)
        print(f"Inserted {len(today_data)} records into today's collection in MongoDB")

        # Insert new data into yesterday's collection
        yesterday_collection.insert_many(yesterday_data)
        print(f"Inserted {len(yesterday_data)} records into yesterday's collection in MongoDB")

    def save_to_file(self, data, filename):
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4, cls=DateTimeEncoder)

    def create_trigger_file(self, trigger_file):
        with open(trigger_file, 'w') as f:
            pass
        print(f"Created trigger file: {trigger_file}")



    @staticmethod
    def get_mongodb_uri(file_path):
        try:
            with open(file_path, 'r') as file:
                mongodb_uri = file.read().strip()
                if not mongodb_uri:
                    raise ValueError("The file is empty or contains only whitespace.")
                return mongodb_uri
        except FileNotFoundError:
            raise FileNotFoundError(f"The file at {file_path} was not found.")
        except Exception as e:
            raise RuntimeError(f"An error occurred while reading the file: {str(e)}")

    @staticmethod
    def get_mongodb_db(file_path):
        try:
            with open(file_path, 'r') as file:
                mongodb_db = file.read().strip()
                if not mongodb_db:
                    raise ValueError("The file is empty or contains only whitespace.")
                return mongodb_db
        except FileNotFoundError:
            raise FileNotFoundError(f"The file at {file_path} was not found.")
        except Exception as e:
            raise RuntimeError(f"An error occurred while reading the file: {str(e)}")

    @staticmethod
    def get_mongodb_uri():
        uri = MongoHandler.get_mongodb_uri("mongoUri.txt")
        return uri

# Usage example
if __name__ == "__main__":
    today_filename = "ranked_crypto_data.json"
    yesterday_prices_filename = "yesterday_price_change.json"
    mongo_uri = CryptoMongoLoader.get_mongodb_uri("mongoUri.txt")
    db_name = CryptoMongoLoader.get_mongodb_db("mongoDB.txt")
    today_collection_name = "crypto_tokens"
    yesterday_collection_name = "yesterday_coins"

    crypto_loader = CryptoMongoLoader(today_filename, yesterday_prices_filename, mongo_uri, db_name, today_collection_name, yesterday_collection_name)
    today_processed_data = crypto_loader.process_today_data()
    yesterday_processed_data = crypto_loader.process_yesterday_data()

    # Load data into MongoDB
    crypto_loader.load_to_mongo(today_processed_data, yesterday_processed_data)

    # Save the processed today data to yesterday's data file
    yesterday_filename = "yesterday_data.json"
    crypto_loader.save_to_file(today_processed_data, yesterday_filename)
    print("Data processed and saved successfully.")

    # Create the trigger file
    trigger_file = "trigger_file.txt"
    crypto_loader.create_trigger_file(trigger_file)
