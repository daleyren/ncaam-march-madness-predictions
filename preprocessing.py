years = [year for year in range(2008, 2025 + 1)]
# years = [2025]

import pandas as pd
import numpy as np

for i, year in enumerate(years):
    games_df = pd.read_csv(f'game-data/{year}games.csv', index_col='Unnamed: 0')

    def parse_result(result):
        result_parts = result.split(', ')
        outcome = result_parts[0]  # W or L
        scores = list(map(int, result_parts[1].split('-')))
        
        if outcome == 'W':
            team_points = max(scores)
            opponent_points = min(scores)
        else:
            team_points = min(scores)
            opponent_points = max(scores)
        
        return pd.Series([outcome, team_points, opponent_points])

    games_df[['Result', 'Team Points', 'Opponent Points']] = games_df['Result'].apply(parse_result)
    games_df['Point Differential'] = games_df['Team Points'] - games_df['Opponent Points']

    games_df['Date'] = pd.to_datetime(games_df['Date'])
    games_df = games_df.sort_values('Date')

    # Columns to drop:
    #   Rank, Game ID, Season Year, Game Breakdown, Extra
    games_df = games_df.drop(columns = ['Rank', 'Game ID', 'Season Year', 'Game Breakdown', 'Extra'])

    try:
        games_df.to_csv(f'game-data/{year}games.csv')    
        print(f'{i + 1}/{len(years)} | successfully preprocessed games from {year}')
    except Exception as e:
        print('ERROR:', e)

