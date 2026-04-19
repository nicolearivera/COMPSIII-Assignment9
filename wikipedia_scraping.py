import requests
import re
import sqlite3
from bs4 import BeautifulSoup

# -----------------------
# DATABASE SETUP (MATCH TESTS EXACTLY)
# -----------------------
connection = sqlite3.connect("movies.db")
cursor = connection.cursor()

cursor.execute("DROP TABLE IF EXISTS movies;")

cursor.execute("""
CREATE TABLE movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    worldwide_gross INTEGER,
    year INTEGER
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

    movies = []

    for table in tables:
        headers_row = table.find("tr")
        if not headers_row:
            continue

        headers = [h.get_text(strip=True).lower() for h in headers_row.find_all(["th", "td"])]

        # must contain correct table headers
        if not ("title" in headers and "worldwide gross" in headers and "year" in headers):
            continue

        rows = table.find_all("tr")[1:]

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 5:
                continue

            try:
                # safer extraction by position fallback
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

                year = int(year_match.group())

                movies.append({
                    "title": title,
                    "worldwide_gross": worldwide_gross,
                    "year": year
                })

                if len(movies) == 50:
                    return movies

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