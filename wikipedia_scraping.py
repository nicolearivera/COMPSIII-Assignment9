# Write your code here
import requests
import re
import sqlite3
from bs4 import BeautifulSoup

# -----------------------
# DATABASE SETUP
# -----------------------
connection = sqlite3.connect("movies.db")
cursor = connection.cursor()

cursor.execute('''DROP TABLE IF EXISTS movies;''')

cursor.execute('''
CREATE TABLE movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    worldwide_gross INTEGER,
    year TEXT
);
''')

# -----------------------
# SCRAPE FUNCTION
# -----------------------
def scrape_wikipedia():
    url = "https://en.wikipedia.org/wiki/List_of_highest-grossing_films"

    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", class_="wikitable")
    rows = table.find_all("tr")

    movies = []

    for row in rows[1:]:
        cols = row.find_all("td")

        # correct table has at least 5 columns
        if len(cols) < 5:
            continue

        try:
            title = cols[2].text.strip()
            gross_text = cols[3].text.strip()
            year_text = cols[4].text.strip()

            # clean gross
            gross_clean = re.sub(r"[^0-9]", "", gross_text)
            if not gross_clean:
                continue

            worldwide_gross = int(gross_clean)

            # extract year as STRING (required by tests)
            year_match = re.search(r"\d{4}", year_text)
            if not year_match:
                continue

            year = year_match.group()

            movies.append({
                "title": title,
                "worldwide_gross": worldwide_gross,
                "year": year
            })

            if len(movies) == 50:
                break

        except:
            continue

    return movies

# -----------------------
# INSERT INTO DATABASE
# -----------------------
data = scrape_wikipedia()

for movie in data:
    cursor.execute('''
        INSERT INTO movies (title, worldwide_gross, year)
        VALUES (?, ?, ?)
    ''', (
        movie["title"],
        movie["worldwide_gross"],
        movie["year"]
    ))

# -----------------------
# COMMIT
# -----------------------
connection.commit()

