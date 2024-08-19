import subprocess
import os
import time


def run_script(script_name, output_file=None):
    result = subprocess.run(["python", script_name], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"{script_name} ran successfully.")
        if output_file:
            wait_for_file(output_file)
    else:
        print(f"Error running {script_name}.")
        print(result.stderr)


def wait_for_file(filepath, timeout=60):
    start_time = time.time()
    while not os.path.exists(filepath):
        if time.time() - start_time > timeout:
            print(f"Timeout waiting for file {filepath}")
            break
        time.sleep(1)
    if os.path.exists(filepath):
        print(f"File {filepath} is ready.")


if __name__ == "__main__":
    new_listing_run_scripts_with_output_files = [
        ("SeleniumScraper.py", "pruned_data.json"),
        ("TwitterScraper.py", "filtered_twitter_data.json"),
        ("CryptoRanker.py", "ranked_crypto_data.json"),
        ("YesterdayCoins.py", "yesterday_price_change.json"),
        ("crypto_mongo_loader.py", "trigger_file.txt")
    ]

    for script, output_file in new_listing_run_scripts_with_output_files:
        run_script(script, output_file)

    cleanup_script = "FileCleanup.py"

    run_script(cleanup_script)


