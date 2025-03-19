import requests
import pandas as pd

years = [year for year in range(2008, 2024 + 1)]
# years = [2008]

columns = [
    "Date", "Rank", "Team", "Conference", "Opponent", "Venue", "Result", "AdjO", "AdjD", "EffO", 
    "eFG%", "TO%", "Reb%", "FTR", "EffD", "Opp eFG%", "Opp TO%", "Opp Reb%", "Opp FTR", "G-SC", 
    "Opponent Conference", "Game ID", "Season Year", "Game Tempo", "Game Unique ID", "Coach", 
    "Opponent Coach", "Unknown", "Game Importance", "Game Breakdown", "Extra"
]

for i, year in enumerate(years):
    url = f'https://barttorvik.com/getgamestats.php?sIndex=7&year={year}&tvalue=All&cvalue=All&opcvalue=All&ovalue=All&minwin=All&mindate=&maxdate=&typev=All&venvalue=All&minadjo=0&minadjd=200&mintempo=0&minppp=0&minefg=0&mintov=200&minreb=0&minftr=0&minpppd=200&minefgd=200&mintovd=0&minrebd=200&minftrd=200&mings=0&mingscript=-100&maxx=100&coach=All&opcoach=All&adjoSelect=min&adjdSelect=max&tempoSelect=min&pppSelect=min&efgSelect=min&tovSelect=max&rebSelect=min&ftrSelect=min&pppdSelect=max&efgdSelect=max&tovdSelect=min&rebdSelect=max&ftrdSelect=max&gscriptSelect=min&sortToggle=1'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data, columns=columns)
        try:
            df.to_csv(f'game-data/{year}games.csv')
            print(f'{i + 1}/{len(years)} | successfullsy scraped games from {year}')
        except Exception as e:
            print('ERROR:', e)
    else:
        print(f"Error: {response.status_code}, {response.text}")
