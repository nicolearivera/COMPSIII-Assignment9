import requests
import re
import sqlite3
from bs4 import BeautifulSoup

# -----------------------
# DATABASE SETUP
# -----------------------
connection = sqlite3.connect("movies.db")
cursor = connection.cursor()

cursor.execute("DROP TABLE IF EXISTS movies;")

cursor.execute("""
CREATE TABLE movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    worldwide_gross INTEGER,
    year TEXT
);
""")

# -----------------------
# SCRAPER
# -----------------------
def scrape_wikipedia():
    url = "https://en.wikipedia.org/wiki/List_of_highest-grossing_films"
    headers = {"User-Agent": "Mozilla/5.0"}

    html = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html, "html.parser")

    tables = soup.find_all("table", class_="wikitable")

    target_table = None

    # pick correct table by structure (NOT filtering data)
    for table in tables:
        header = table.find("tr")
        if not header:
            continue

        if "Worldwide gross" in header.get_text() and "Year" in header.get_text():
            target_table = table
            break

    if target_table is None:
        return []

    rows = target_table.find_all("tr")

    movies = []

    for row in rows[1:]:
        cols = row.find_all("td")

        if len(cols) < 5:
            continue

        try:
            title = cols[2].get_text(strip=True)

            gross_text = cols[3].get_text(strip=True)
            gross_clean = re.sub(r"[^0-9]", "", gross_text)

            if not gross_clean:
                continue

            worldwide_gross = int(gross_clean)

            year_text = cols[4].get_text(strip=True)
            year_match = re.search(r"\d{4}", year_text)

            if not year_match:
                continue

            year = year_match.group()   # STRING (IMPORTANT FIX)

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
    cursor.execute("""
        INSERT INTO movies (title, worldwide_gross, year)
        VALUES (?, ?, ?)
    """, (movie["title"], movie["worldwide_gross"], movie["year"]))

connection.commit()