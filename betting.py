def test_betting_stategy(predictions, test_features, test_labels, bet_difference=0.05):
    result = {
        'spend': 0,
        'return': 0,
    }

    for i in range(0, len(predictions)):
        probabilities = predictions[i]['probabilities']

        bets = []

        if probabilities[0] > (1 / test_features['odds-home'][i]) + bet_difference:
            bets.append(['H', test_features['odds-home'][i]])

        if probabilities[2] > (1 / test_features['odds-away'][i]) + bet_difference:
            bets.append(['A', test_features['odds-away'][i]])

        if probabilities[1] > (1 / test_features['odds-draw'][i]) + bet_difference:
            bets.append(['D', test_features['odds-away'][i]])

        for bet in bets:
            result['spend'] = result['spend'] + 1

            if test_labels[i] == bet[0]:
                result['return'] = result['return'] + bet[1]

    result['performance'] = result['return'] / result['spend']

    return result
