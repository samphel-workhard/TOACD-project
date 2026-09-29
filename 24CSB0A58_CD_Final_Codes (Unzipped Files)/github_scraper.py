import requests
import time
import csv

# The list of high-risk keywords used in your secure_scan.py guardrails
RISK_KEYWORDS = [
    "strcpy", "sprintf", "gets", "system", "exec", "popen"
]

import os

# Note: Unauthenticated requests are limited to 10 per minute. 
# If you have a GitHub Personal Access Token (PAT), add it here for 30 req/min!
HEADERS = {
    "Accept": "application/vnd.github.v3+json"
}
github_token = os.environ.get("GITHUB_TOKEN")
if github_token:
    HEADERS["Authorization"] = f"Bearer {github_token}"

def get_keyword_frequency(keyword):
    """Hits the GitHub Search API and returns the total count of files containing the keyword."""
    # We restrict the search to C++ files to keep your data highly relevant
    query = f"{keyword} language:cpp"
    url = f"https://api.github.com/search/code?q={query}"
    
    print(f"🔍 Searching GitHub for: '{keyword}'...")
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        return data.get("total_count", 0)
    elif response.status_code == 403:
        print("⚠️ Rate limit hit! Waiting 60 seconds...")
        time.sleep(60)
        return get_keyword_frequency(keyword) # Retry
    else:
        print(f"❌ Error fetching {keyword}: {response.status_code}")
        return 0

if __name__ == "__main__":
    print("🚀 Starting GitHub Security Keyword Miner...\n")
    
    results = []
    for word in RISK_KEYWORDS:
        count = get_keyword_frequency(word)
        results.append({"Keyword": word, "GitHub_Occurrences": count})
        # Sleep for 6 seconds between requests to respect GitHub's unauthenticated rate limits
        time.sleep(6) 
        
    # Export the findings to a CSV for your Mid-Evaluation
    csv_filename = "github_risk_data.csv"
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["Keyword", "GitHub_Occurrences"])
        writer.writeheader()
        writer.writerows(results)
        
    print(f"\n✅ Data collection complete! Dataset saved as '{csv_filename}'.")