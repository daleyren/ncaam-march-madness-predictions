from bs4 import BeautifulSoup
import selenium
import requests
import pandas as pd
import numpy
from datetime import datetime, timedelta
import time
import random

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

# from https://www.sslproxies.org/
PROXIES = [
    "27.79.203.133:16000",
    "216.229.112.25:8080",
    "52.73.224.54:3128",
    "35.71.150.105:8080",
    "63.35.64.177:3128",
    "54.248.238.110:80",
    "184.168.124.233:5402",
    "86.106.132.186:3128",
    "45.140.143.77:18080",
    "54.152.3.36:80",
    "51.20.19.159:3128"
]


def get_proxy():
    proxy = random.choice(PROXIES)
    return {"http": f"http://{proxy}", "https": f"https://{proxy}"}

def fetch_page(url, max_retries=5):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            
            if response.status_code == 200:
                return response  # Success

            print(f"Attempt {attempt+1}/{max_retries} failed with status {response.status_code}. Retrying...")

        except Exception as e:
            print(e)
            
        time.sleep(random.uniform(3, 10))  # Random delay to avoid detection

    print(f"Max retries reached for {url}. Skipping...")
    return None  # Failed after max retries


def scrape():    
    years = [year for year in range(2015, 2025)]
    season_dates = {
        2015: ("2016-02-08", "2016-04-05"), # 2015: ("2015-11-13", "2016-04-05"),
        2016: ("2016-11-11", "2017-04-04"),
        2017: ("2017-11-10", "2018-04-01"),
        2018: ("2018-11-09", "2019-04-07"),
        2019: ("2019-11-08", "2020-04-05"),
        2020: ("2020-11-25", "2021-04-04"),
        2021: ("2021-11-09", "2022-04-03"),
        2022: ("2022-11-07", "2023-04-02"),
        2023: ("2023-11-06", "2024-04-07"),
        2024: ("2024-11-04", "2025-03-19")
    }
    
    for i, year in enumerate(years[9:]):
        start_date, end_date = season_dates[year]
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

        DATE = []
        TEAM_A = []
        TEAM_B = []
        TEAM_A_POINTS = []
        TEAM_B_POINTS = []
        WINNER = []
        POINT_DIFFERENTIAL = []

        curr_datetime = start_datetime
        # difference_in_days = (end_datetime - start_datetime).days

        j = 0
        while curr_datetime <= end_datetime:
            curr_year = curr_datetime.year
            curr_month = curr_datetime.month
            curr_day = curr_datetime.day
            # print(curr_year, curr_month, curr_day)
            curr_datetime += timedelta(days=1)

            URL = f"https://www.sports-reference.com/cbb/boxscores/index.cgi?month={curr_month}&day={curr_day}&year={curr_year}"

            # print(URL)
            # proxy = get_proxy()
            # page = requests.get(URL, proxies=proxy, headers=HEADERS)

            page = fetch_page(URL)
            if page is None:
                # Save Data
                data = {
                    'Date': DATE,
                    'Team A': TEAM_A,
                    'Team B': TEAM_B,
                    'Team A Points': TEAM_A_POINTS,
                    'Team B Points': TEAM_B_POINTS,
                    'Winner': WINNER,
                    'Point Differential': POINT_DIFFERENTIAL
                }
                df = pd.DataFrame(data)

                prev_df = pd.read_csv(f'game-data/{year}games.csv')
                new_df = pd.concat([prev_df, df])
                new_df.to_csv(f'game-data/{year}games.csv')

                raise Exception("Connection Error from fetch_page call")

            soup = BeautifulSoup(page.content, "html.parser")
            all_womens_games = soup.find_all("div", class_="game_summary nohover gender-f")
            
            # Hits Rate Limited Request Page
            if soup.find("h1") and soup.find("h1").text == 'Rate Limited Request (429 error)':
                # Save Data
                data = {
                    'Date': DATE,
                    'Team A': TEAM_A,
                    'Team B': TEAM_B,
                    'Team A Points': TEAM_A_POINTS,
                    'Team B Points': TEAM_B_POINTS,
                    'Winner': WINNER,
                    'Point Differential': POINT_DIFFERENTIAL
                }
                df = pd.DataFrame(data)

                prev_df = pd.read_csv(f'game-data/{year}games.csv')
                new_df = pd.concat([prev_df, df], ignore_index=True)
                new_df.to_csv(f'game-data/{year}games.csv')

                raise Exception("Rate Limited Requests (429 Error); next: " + f'{curr_year}-{curr_month}-{curr_day}')
            for curr_womens_game in all_womens_games:
                # Winner Parse
                winner_tr = curr_womens_game.find("tr", class_="winner")
                winner_team = winner_tr.find("a").text
                winner_score = int(winner_tr.find("td", class_="right").text)
                
                # Loser Parse
                loser_tr = curr_womens_game.find("tr", class_="loser")
                loser_team = loser_tr.find("a").text
                loser_score = int(loser_tr.find("td", class_="right").text)

                # Additional Feature(s)
                point_diff = winner_score - loser_score
                
                DATE.append(f'{curr_year}-{curr_month}-{curr_day}')
                TEAM_A.append(winner_team)
                TEAM_B.append(loser_team)
                TEAM_A_POINTS.append(winner_score)
                TEAM_B_POINTS.append(loser_score)
                WINNER.append(winner_team)
                POINT_DIFFERENTIAL.append(point_diff)
            j += 1
            print(f'{curr_year}-{curr_month}-{curr_day}')
            time.sleep(10)

            
        data = {
            'Date': DATE,
            'Team A': TEAM_A,
            'Team B': TEAM_B,
            'Team A Points': TEAM_A_POINTS,
            'Team B Points': TEAM_B_POINTS,
            'Winner': WINNER,
            'Point Differential': POINT_DIFFERENTIAL
        }
        df = pd.DataFrame(data)

        prev_df = pd.read_csv(f'game-data/{year}games.csv', index_col='Unnamed: 0')
        new_df = pd.concat([prev_df, df], ignore_index=True)
        new_df.to_csv(f'game-data/{year}games.csv')

        print(f'{i+1}/{len(years)} successfully scraped - {year}')


def main():
    scrape()


if __name__=="__main__":
    main()