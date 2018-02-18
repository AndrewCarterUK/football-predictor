import csv
import datetime
from functools import reduce


def get_results(file_path):
    results = []
        
    with open(file_path) as stream:
        reader = csv.DictReader(stream)

        for row in reader:
            row['Date'] = datetime.datetime.strptime(row['Date'], '%d/%m/%y')
            results.append(row)

    return results


def get_previous_results(results, team, date):
    def filter_fn(result):
        return (
            result['HomeTeam'] == team or
            result['AwayTeam'] == team
        ) and (result['Date'] < date)

    def map_fn(result):
        if result['HomeTeam'] == team:
            return {
                'win': 1 if result['FTR'] == 'H' else 0,
                'draw': 1 if result['FTR'] == 'D' else 0,
                'lose': 1 if result['FTR'] == 'A' else 0,
                'goals': int(result['FTHG']),
                'goals-conceeded': int(result['FTAG']),
                'shots': int(result['HS']),
                'shots-conceeded': int(result['AS']),
                'shots-accuracy': int(result['HST']) / (1 + int(result['HS'])),
                'shots-accuracy-conceeded': int(result['AST']) / (1 + int(result['AS']))
            }
        else:  # Away Team
            return {
                'win': 1 if result['FTR'] == 'A' else 0,
                'draw': 1 if result['FTR'] == 'D' else 0,
                'lose': 1 if result['FTR'] == 'H' else 0,
                'goals': int(result['FTAG']),
                'goals-conceeded': int(result['FTHG']),
                'shots': int(result['AS']),
                'shots-conceeded': int(result['HS']),
                'shots-accuracy': int(result['AST']) / (1 + int(result['AS'])),
                'shots-accuracy-conceeded': int(result['HST']) / (1 + int(result['HS'])),
            }

    return list(map(map_fn, filter(filter_fn, results)))


def get_dataset(file_path):
    results = get_results(file_path)

    dataset = []

    def reduce_fn(x, y):
        result = {}

        for key in x.keys():
            result[key] = x[key] + y[key]

        return result

    for result in results:
        previous_home_results = get_previous_results(results, result['HomeTeam'], result['Date'])
        previous_away_results = get_previous_results(results, result['AwayTeam'], result['Date'])

        if len(previous_home_results) < 5 or len(previous_away_results) < 5:
            continue

        last_5_home_results = reduce(reduce_fn, previous_home_results[-5:])
        last_5_away_results = reduce(reduce_fn, previous_away_results[-5:])

        combined = {
            'result': result['FTR'],
            'odds-home': float(result['B365H']),
            'odds-draw': float(result['B365D']),
            'odds-away': float(result['B365A']),
        }

        for key in last_5_home_results.keys():
            combined['home-' + key] = last_5_home_results[key]
            combined['away-' + key] = last_5_away_results[key]

        dataset.append(combined)

    return dataset
