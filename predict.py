import dataset
import betting
import tensorflow as tf
import numpy as np
import csv

TRAINING_SET_FRACTION = 0.95


def main(argv):
    data = dataset.Dataset('data/book.csv')

    train_results_len = int(TRAINING_SET_FRACTION * len(data.processed_results))
    train_results = data.processed_results[:train_results_len]
    test_results = data.processed_results[train_results_len:]

    def map_results(results):
        features = {}

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
            tf.feature_column.numeric_column(key='{}-wins'.format(mode)),
            tf.feature_column.numeric_column(key='{}-draws'.format(mode)),
            tf.feature_column.numeric_column(key='{}-losses'.format(mode)),
            tf.feature_column.numeric_column(key='{}-goals'.format(mode)),
            tf.feature_column.numeric_column(key='{}-opposition-goals'.format(mode)),
            tf.feature_column.numeric_column(key='{}-shots'.format(mode)),
            tf.feature_column.numeric_column(key='{}-shots-on-target'.format(mode)),
            tf.feature_column.numeric_column(key='{}-opposition-shots'.format(mode)),
            tf.feature_column.numeric_column(key='{}-opposition-shots-on-target'.format(mode)),
        ]

    model = tf.estimator.DNNClassifier(
        model_dir='model/',
        hidden_units=[10],
        feature_columns=feature_columns,
        n_classes=3,
        label_vocabulary=['H', 'D', 'A'],
        optimizer=tf.train.ProximalAdagradOptimizer(
            learning_rate=0.1,
            l1_regularization_strength=0.001
        ))

    with open('training-log.csv', 'w') as stream:
        csvwriter = csv.writer(stream)

        for i in range(0, 200):
            model.train(input_fn=train_input_fn, steps=100)
            evaluation_result = model.evaluate(input_fn=test_input_fn)

            predictions = list(model.predict(input_fn=test_input_fn))
            prediction_result = betting.test_betting_stategy(predictions, test_features, test_labels)

            csvwriter.writerow([(i + 1) * 100, evaluation_result['accuracy'], evaluation_result['average_loss'], prediction_result['performance']])


if __name__ == '__main__':
    tf.logging.set_verbosity(tf.logging.INFO)
    tf.app.run(main=main)
