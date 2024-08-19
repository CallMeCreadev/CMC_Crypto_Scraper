import os
import json

def delete_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
        else:
            print(f"File does not exist: {file_path}")
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")


if __name__ == "__main__":
    files_to_delete = [
        "pruned_data.json",
        "filtered_twitter_data.json",
        "ranked_crypto_data.json",
        "yesterday_price_change.json",
        "trigger_file.txt"
    ]

    for file in files_to_delete:
        delete_file(file)
