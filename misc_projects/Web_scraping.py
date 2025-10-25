import requests
from bs4 import BeautifulSoup
import pandas as pd

# Step 1: Fetch the HTML content
url = "https://github.com/trending"
response = requests.get(url)
if response.status_code != 200:
    raise Exception("Failed to fetch page")

# Step 2: Parse HTML using BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser")
repos = soup.find_all("article", class_="Box-row")

# Step 3: Extract data
data = []
for repo in repos:
    # Repository name and developer
    full_name = repo.h2.a.get("href").strip("/")  # e.g., 'owner/repo'
    owner, name = full_name.split("/")

    # Language (may not be present)
    lang_tag = repo.find("span", itemprop="programmingLanguage")
    language = lang_tag.text.strip() if lang_tag else "N/A"

    # Stars (simplified parsing)
    stars_tag = repo.find("a", href=lambda x: x and x.endswith("/stargazers"))
    stars = stars_tag.text.strip().replace(",", "") if stars_tag else "0"

    data.append({
        "Owner": owner,
        "Repository": name,
        "Language": language,
        "Stars": stars
    })

# Step 4: Create DataFrame
df = pd.DataFrame(data)
print(df.head())

# Step 5: Optional — Save to CSV
df.to_csv(r"C:\Users\kpras\Desktop\Test_data\github_trending.csv", index=False)
print("Data saved to github_trending.csv")
