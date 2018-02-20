import csv
import datetime
from functools import reduce


class Dataset:
    def __init__(self, file_path):
        self.raw_results = []
        self.processed_results = []

        with open(file_path) as stream:
            reader = csv.DictReader(stream)

            for row in reader:
                row['Date'] = datetime.datetime.strptime(row['Date'], '%d/%m/%y')
                self.raw_results.append(row)

        for result in self.raw_results:
            home_statistics = self.get_statistics(result['HomeTeam'], result['Date'])

            if home_statistics is None:
                continue

            away_statistics = self.get_statistics(result['AwayTeam'], result['Date'])

            if away_statistics is None:
                continue

            processed_result = {
                'result': result['FTR'],
                'odds-home': float(result['B365H']),
                'odds-draw': float(result['B365D']),
                'odds-away': float(result['B365A']),
            }

            for label, statistics in [('home', home_statistics), ('away', away_statistics)]:
                for key in statistics.keys():
                    processed_result[label + '-' + key] = statistics[key]

            self.processed_results.append(processed_result)

    # Filter results to only contain matches played in by a given team, before a given date
    def filter(self, team, date):
        def filter_fn(result):
            return (
                result['HomeTeam'] == team or
                result['AwayTeam'] == team
            ) and (result['Date'] < date)

        return list(filter(filter_fn, self.raw_results))

    # Calculate team statistics
    def get_statistics(self, team, date, matches=10):
        recent_results = self.filter(team, date)

        if len(recent_results) < matches:
            return None

        # This function maps a result to a set of performance measures roughly scaled between -1 and 1
        def map_fn(result):
            if result['HomeTeam'] == team:
                team_letter, opposition_letter = 'H', 'A'
                opposition = result['AwayTeam']
            else:
                team_letter, opposition_letter = 'A', 'H'
                opposition = result['HomeTeam']

            goals = int(result['FT{}G'.format(team_letter)])
            shots = int(result['{}S'.format(team_letter)])
            shots_on_target = int(result['{}ST'.format(team_letter)])
            shot_accuracy = shots_on_target / shots if shots > 0 else 0

            opposition_goals = int(result['FT{}G'.format(opposition_letter)])
            opposition_shots = int(result['{}S'.format(opposition_letter)])
            opposition_shots_on_target = int(result['{}ST'.format(opposition_letter)])

            return {
                'wins': 1 if result['FTR'] == team_letter else 0,
                'draws': 1 if result['FTR'] == 'D' else 0,
                'losses': 1 if result['FTR'] == opposition_letter else 0,
                'goals': int(result['FT{}G'.format(team_letter)]),
                'opposition-goals': int(result['FT{}G'.format(opposition_letter)]),
                'shots': int(result['{}S'.format(team_letter)]),
                'shots-on-target': int(result['{}ST'.format(team_letter)]),
                'opposition-shots': int(result['{}S'.format(opposition_letter)]),
                'opposition-shots-on-target': int(result['{}ST'.format(opposition_letter)]),
            }

        def reduce_fn(x, y):
            result = {}

            for key in x.keys():
                result[key] = x[key] + y[key]

            return result

        return reduce(reduce_fn, map(map_fn, recent_results[-matches:]))
