def test_betting_stategy(predictions, test_features, test_labels, bet_difference=0.05):
    result = {
        'spend': 0,
        'return': 0,
    }

    for i in range(0, len(predictions)):
        probabilities = predictions[i]['probabilities']

        if probabilities[1] > (1 / test_features['odds-draw'][i]) + bet_difference:
            result['spend'] = result['spend'] + 1

            if test_labels[i] == 'D':
                result['return'] = result['return'] + test_features['odds-draw'][i]

    result['performance'] = result['return'] / result['spend']

    return result
