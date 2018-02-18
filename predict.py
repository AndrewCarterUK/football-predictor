import dataset
import betting
import pprint
import tensorflow as tf
import numpy as np

TRAINING_SET_FRACTION = 0.95


def main(argv):
    data = dataset.get_dataset('data/book.csv')

    train_results_len = int(TRAINING_SET_FRACTION * len(data))
    train_results = data[:train_results_len]
    test_results = data[train_results_len:]

    def map_results(results):
        features = {}
        labels = []

        for result in results:
            for key in result.keys():
                if key not in features:
                    features[key] = []

                features[key].append(result[key])

        for key in features.keys():
            features[key] = np.array(features[key])

        return features, features['result']

    train_features, train_labels = map_results(train_results)
    test_features, test_labels = map_results(test_results)

    train_input_fn = tf.estimator.inputs.numpy_input_fn(
        x=train_features,
        y=train_labels,
        batch_size=500,
        num_epochs=None,
        shuffle=True
    )

    test_input_fn = tf.estimator.inputs.numpy_input_fn(
        x=test_features,
        y=test_labels,
        num_epochs=1,
        shuffle=False
    )

    feature_columns = []

    for mode in ['home', 'away']:
        feature_columns = feature_columns + [
            tf.feature_column.numeric_column(key='{}-win'.format(mode)),
            tf.feature_column.numeric_column(key='{}-lose'.format(mode)),
            tf.feature_column.numeric_column(key='{}-draw'.format(mode)),
            tf.feature_column.numeric_column(key='{}-goals'.format(mode)),
            tf.feature_column.numeric_column(key='{}-goals-conceeded'.format(mode)),
            tf.feature_column.numeric_column(key='{}-shots'.format(mode)),
            tf.feature_column.numeric_column(key='{}-shots-conceeded'.format(mode)),
            tf.feature_column.numeric_column(key='{}-shots-accuracy'.format(mode)),
            tf.feature_column.numeric_column(key='{}-shots-accuracy-conceeded'.format(mode)),
        ]

    model = tf.estimator.DNNClassifier(
        model_dir='model/',
        hidden_units=[10],
        feature_columns=feature_columns,
        n_classes=3,
        label_vocabulary=['H', 'D', 'A'])

    for i in range(0, 20):
        model.train(input_fn=train_input_fn, steps=1000)
        model.evaluate(input_fn=test_input_fn)

        predictions = list(model.predict(input_fn=test_input_fn))
        prediction_result = betting.test_betting_stategy(predictions, test_features, test_labels)
        pprint.pprint(prediction_result)


if __name__ == '__main__':
    tf.logging.set_verbosity(tf.logging.INFO)
    tf.app.run(main=main)
