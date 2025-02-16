import os
import sys
import pytest
from lark import Lark, exceptions

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import ModelTransformer, create_parser

@pytest.fixture
def layer_parser():
    return create_parser('layer')

@pytest.fixture
def network_parser():
    return create_parser('network')

@pytest.fixture
def research_parser():
    return create_parser('research')

@pytest.fixture
def transformer():
    return ModelTransformer()


@pytest.mark.parametrize(
    "layer_string,expected,test_id",
    [
        ('Dense(128, "relu")', {'type': 'Dense', 'params': {'units': 128, 'activation': 'relu'}}, "dense-relu"),
        ('Dense(units=256, activation="sigmoid")', {'type': 'Dense', 'params': {'units': 256, 'activation': 'sigmoid'}}, "dense-sigmoid"),
        ('Conv2D(32, (3, 3), "relu")', {'type': 'Conv2D', 'params': {'filters': 32, 'kernel_size': (3, 3), 'activation': 'relu'}}, "conv2d-relu"),
        ('Conv2D(filters=64, kernel_size=(5, 5), activation="tanh")', {'type': 'Conv2D', 'params': {'filters': 64, 'kernel_size': (5, 5), 'activation': 'tanh'}}, "conv2d-tanh"),
        ('Conv2D(filters=32, kernel_size=3, activation="relu", padding="same")', {'type': 'Conv2D', 'params': {'filters': 32, 'kernel_size': 3, 'activation': 'relu', 'padding': 'same'}}, "conv2d-padding"),
        ('MaxPooling2D(pool_size=(2, 2))', {'type': 'MaxPooling2D', 'params': {'pool_size': (2, 2)}}, "maxpooling2d"),
        ('MaxPooling2D((3, 3), 2, "valid")', {'type': 'MaxPooling2D', 'params': {'pool_size': (3, 3), 'strides': 2, 'padding': 'valid'}}, "maxpooling2d-strides"),
        ('Flatten()', {'type': 'Flatten', 'params': None}, "flatten"),
        ('Dropout(0.5)', {'type': 'Dropout', 'params': {'rate': 0.5}}, "dropout"),
        ('Dropout(rate=0.25)', {'type': 'Dropout', 'params': {'rate': 0.25}}, "dropout-named"),
        ('BatchNormalization()', {'type': 'BatchNormalization', 'params': None}, "batchnorm"),
        ('LayerNormalization()', {'type': 'LayerNormalization', 'params': None}, "layernorm"),
        ('InstanceNormalization()', {'type': 'InstanceNormalization', 'params': None}, "instancenorm"),
        ('GroupNormalization(groups=32)', {'type': 'GroupNormalization', 'params': {'groups': 32}}, "groupnorm"),
        ('LSTM(units=64)', {'type': 'LSTM', 'params': {'units': 64}}, "lstm"),
        ('LSTM(units=128, return_sequences=true)', {'type': 'LSTM', 'params': {'units': 128, 'return_sequences': True}}, "lstm-return"),
        ('GRU(units=32)', {'type': 'GRU', 'params': {'units': 32}}, "gru"),
        ('SimpleRNN(units=16)', {'type': 'SimpleRNN', 'params': {'units': 16}}, "simplernn"),
        ('LSTM(units=256)', {'type': 'LSTM', 'params': {'units': 256}}, "lstm-cudnn"),  # Corrected CudnnLSTM to LSTM
        ('GRU(units=128)', {'type': 'GRU', 'params': {'units': 128}}, "gru-cudnn"),  # Corrected CudnnGRU to GRU
        ('RNNCell(units=32)', {'type': 'RNNCell', 'params': {'units': 32}}, "rnncell"),
        ('LSTMCell(units=64)', {'type': 'LSTMCell', 'params': {'units': 64}}, "lstmcell"),
        ('GRUCell(units=128)', {'type': 'GRUCell', 'params': {'units': 128}}, "grucell"),
        ('SimpleRNNDropoutWrapper(units=16, dropout=0.3)', {'type': 'SimpleRNNDropoutWrapper', 'params': {'units': 16, 'dropout': 0.3}}, "simplernn-dropout"),
        ('GRUDropoutWrapper(units=32, dropout=0.4)', {'type': 'GRUDropoutWrapper', 'params': {'units': 32, 'dropout': 0.4}}, "gru-dropout"),
        ('LSTMDropoutWrapper(units=64, dropout=0.5)', {'type': 'LSTMDropoutWrapper', 'params': {'units': 64, 'dropout': 0.5}}, "lstm-dropout"),
        ('Attention()', {'type': 'Attention', 'params': None}, "attention"),
        ('TransformerEncoder(num_heads=8, ff_dim=512)', {'type': 'TransformerEncoder', 'params': {'num_heads': 8, 'ff_dim': 512}}, "transformer"),
        ('ResidualConnection()', {'type': 'ResidualConnection', 'params': None}, "residual"),
        ('Inception()', {'type': 'Inception', 'params': None}, "inception"),
        ('CapsuleLayer()', {'type': 'CapsuleLayer', 'params': None}, "capsule"),
        ('SqueezeExcitation()', {'type': 'SqueezeExcitation', 'params': None}, "squeeze"),
        ('GraphConv()', {'type': 'GraphConv', 'params': None}, "graphconv"),
        ('Embedding(input_dim=1000, output_dim=128)', {'type': 'Embedding', 'params': {'input_dim': 1000, 'output_dim': 128}}, "embedding"),
        ('QuantumLayer()', {'type': 'QuantumLayer', 'params': None}, "quantum"),
        ('DynamicLayer()', {'type': 'DynamicLayer', 'params': None}, "dynamic"),
        ('Output(units=10, activation="softmax")', {'type': 'Output', 'params': {'units': 10, 'activation': 'softmax'}}, "output-softmax"),
        ('Output(units=1, activation="sigmoid")', {'type': 'Output', 'params': {'units': 1, 'activation': 'sigmoid'}}, "output-sigmoid"),
        # Edge Cases
        ('Dense(units=0)', {'type': 'Dense', 'params': {'units': 0}}, "dense-zero-units"),  # Edge case: zero units
        ('Dropout(rate=1.0)', {'type': 'Dropout', 'params': {'rate': 1.0}}, "dropout-full"),  # Edge case: full dropout
        ('MaxPooling2D(pool_size=1)', {'type': 'MaxPooling2D', 'params': {'pool_size': 1}}, "maxpool-unit-poolsize"),  # Edge case: pool size of 1
        # Error Cases
        ('Dense(units="abc")', None, "dense-invalid-units"),  # Type error in units
        ('Dropout(2)', None, "dropout-invalid-rate"),  # Type error in rate
        ('InvalidLayerName()', None, "invalid-layer-name"),  # Invalid layer name
    ],
    ids=[
        "dense-relu", "dense-sigmoid", "conv2d-relu", "conv2d-tanh", "conv2d-padding", "maxpooling2d", "maxpooling2d-strides",
        "flatten", "dropout", "dropout-named", "batchnorm", "layernorm", "instancenorm", "groupnorm", "lstm", "lstm-return",
        "gru", "simplernn", "lstm-cudnn", "gru-cudnn", "rnncell", "lstmcell", "grucell", "simplernn-dropout", "gru-dropout",
        "lstm-dropout", "attention", "transformer", "residual", "inception", "capsule", "squeeze", "graphconv", "embedding",
        "quantum", "dynamic", "output-softmax", "output-sigmoid", "dense-zero-units", "dropout-full", "maxpool-unit-poolsize",
        "dense-invalid-units", "dropout-invalid-rate", "invalid-layer-name"
    ]
)
def test_layer_parsing(layer_parser, transformer, layer_string, expected, test_id):

    # Act
    if expected is None:
        with pytest.raises((exceptions.UnexpectedCharacters, exceptions.UnexpectedToken)):  # Expecting parsing error
            layer_parser.parse(layer_string)
    else:
        tree = layer_parser.parse(layer_string)
        result = transformer.transform(tree)

        # Assert
        assert result == expected


@pytest.mark.parametrize(
    "network_string, expected_name, expected_input_shape, expected_layers, expected_loss, expected_optimizer, expected_training_config",
    [
        (
            """
            network TestModel {
                input: (None, 28, 28, 1)
                layers:
                    Conv2D(filters=32, kernel_size=(3,3), activation="relu")
                    MaxPooling2D(pool_size=(2, 2))
                    Flatten()
                    Dense(units=128, activation="relu")
                    Output(units=10, activation="softmax")
                loss: "categorical_crossentropy"
                optimizer: "adam"
                train {
                    epochs: 10
                    batch_size: 32
                }
            }
            """,
            "TestModel", (None, 28, 28, 1),
            [
                {'type': 'Conv2D', 'params': {'filters': 32, 'kernel_size': (3, 3), 'activation': 'relu'}},
                {'type': 'MaxPooling2D', 'params': {'pool_size': (2, 2)}},
                {'type': 'Flatten', 'params': None},
                {'type': 'Dense', 'params': {'units': 128, 'activation': 'relu'}},
                {'type': 'Output', 'params': {'units': 10, 'activation': 'softmax'}}
            ],
            "categorical_crossentropy", "adam", {'epochs': 10, 'batch_size': 32}
        ),
        (
            """
            network SimpleModel {
                input: (28, 28, 1)
                layers:
                    Flatten()
                    Output(units=1, activation="sigmoid")
                loss: "binary_crossentropy"
                optimizer: "SGD"
            }
            """,
            "SimpleModel", (28, 28, 1),
            [
                {'type': 'Flatten', 'params': None},
                {'type': 'Output', 'params': {'units': 1, 'activation': 'sigmoid'}}
            ],
            "binary_crossentropy", "SGD", None  # Empty training config
        ),
        (
            # Edge case: No layers
            """
            network NoLayers {
                input: (10,)
                layers:

                loss: "mse"
                optimizer: "rmsprop"
            }
            """,
            "NoLayers", (10,), [], "mse", "rmsprop", None  # No layers, empty training config
        ),
        (
            # Error case: Invalid input shape
            """
            network InvalidInput {
                input: (28, 28, "abc")
                layers:
                    Dense(10)
                loss: "mse"
                optimizer: "adam"
            }
            """,
            None, None, None, None, None, None  # Expecting parsing error
        ),
    ],
    ids=["complex-model", "simple-model", "no-layers", "invalid-input"]
)
def test_network_parsing(network_parser, transformer, network_string, expected_name, expected_input_shape, expected_layers, expected_loss, expected_optimizer, expected_training_config):

    # Act
    if expected_name is None:
        with pytest.raises((exceptions.UnexpectedCharacters, exceptions.UnexpectedToken)):  # Expecting parsing error
            network_parser.parse(network_string)
    else:
        tree = network_parser.parse(network_string)
        result = transformer.transform(tree)

        # Assert
        assert result['type'] == 'model'
        assert result['name'] == expected_name
        assert result['input'] == {'type': 'Input', 'shape': expected_input_shape}
        assert result['layers'] == expected_layers
        assert result['loss'] == expected_loss
        assert result['optimizer'] == expected_optimizer
        assert result['training_config'] == expected_training_config


@pytest.mark.parametrize(
    "research_string, expected_name, expected_metrics, expected_references",
    [
        (
            """
            research ResearchStudy {
                metrics {
                    accuracy: 0.95
                    loss: 0.05
                }
                references {
                    paper: "Paper Title 1"
                    paper: "Another Great Paper"
                }
            }
            """,
            "ResearchStudy", {'accuracy': 0.95, 'loss': 0.05}, ["Paper Title 1", "Another Great Paper"]
        ),
        (
            """
            research {
                metrics {
                    precision: 0.8
                    recall: 0.9
                }
            }
            """,
            None, {'precision': 0.8, 'recall': 0.9}, []  # No name, no references
        ),
        (
            # Edge case: Empty research block
            """
            research EmptyResearch {
            }
            """,
            "EmptyResearch", None, []
        ),
        (
            # Error case: Invalid metrics
            """
            research InvalidMetrics {
                metrics {
                    accuracy: "high"  # Invalid value type
                }
            }
            """,
            None, None, None  # Expecting parsing error
        ),
    ],
    ids=["complete-research", "no-name-no-ref", "empty-research", "invalid-metrics"]
)
def test_research_parsing(research_parser, transformer, research_string, expected_name, expected_metrics, expected_references):

    # Act
    if expected_name is None:
        with pytest.raises((exceptions.UnexpectedCharacters, exceptions.UnexpectedToken)):  # Expecting parsing error
            research_parser.parse(research_string)
    else:
        tree = research_parser.parse(research_string)
        result = transformer.transform(tree)

        # Assert
        assert result['type'] == 'Research'
        assert result.get('name') == expected_name
        assert result['params'].get('metrics') == expected_metrics
        assert result['params'].get('references') == expected_references

@pytest.mark.parametrize(
    "wrapper_string, expected, test_id",
    [
        (
            'TimeDistributed(Dense(128, activation="relu"), dropout=0.5)',
            {'type': 'TimeDistributed(Dense)', 'params': {'units': 128, 'activation': 'relu', 'dropout': 0.5}},
            "timedistributed-dense"
        )
    ],
    ids=["timedistributed-dense"]
)
def test_wrapper_parsing(layer_parser, transformer, wrapper_string, expected, test_id):
    tree = layer_parser.parse(wrapper_string)
    result = transformer.transform(tree)
    assert result == expected

@pytest.mark.parametrize(
    "lambda_string, expected, test_id",
    [
        (
            'Lambda("x: x * 2")',
            {'type': 'Lambda', 'params': {'function': 'x: x * 2'}},
            "lambda-layer"
        )
    ],
    ids=["lambda-layer"]
)
def test_lambda_parsing(layer_parser, transformer, lambda_string, expected, test_id):
    tree = layer_parser.parse(lambda_string)
    result = transformer.transform(tree)
    assert result == expected

@pytest.mark.parametrize(
    "custom_shape_string, expected, test_id",
    [
        (
            'CustomShape(MyLayer, (32, 32))',
            {"type": "CustomShape", "layer": "MyLayer", "custom_dims": (32, 32)},
            "custom-shape"
        )
    ],
    ids=["custom-shape"]
)
def test_custom_shape_parsing(layer_parser, transformer, custom_shape_string, expected, test_id):
    tree = layer_parser.parse(custom_shape_string)
    result = transformer.transform(tree)
    assert result == expected

@pytest.mark.parametrize(
    "comment_string, expected, test_id",
    [
        (
            'Dense(128, "relu")  # Dense layer with ReLU activation',
            {'type': 'Dense', 'params': {'units': 128, 'activation': 'relu'}},
            "dense-with-comment"
        )
    ],
    ids=["dense-with-comment"]
)
def test_comment_parsing(layer_parser, transformer, comment_string, expected, test_id):
    tree = layer_parser.parse(comment_string)
    result = transformer.transform(tree)
    assert result == expected

@pytest.mark.parametrize(
    "network_string, expected_name, expected_input_shape, expected_layers, expected_loss, expected_optimizer, expected_training_config",
    [
        (
            """
            network OptimizerModel {
                input: (28, 28, 1)
                layers:
                    Dense(64, "relu")
                    Output(units=10, activation="softmax")
                loss: "categorical_crossentropy"
                optimizer: SGD(learning_rate=0.01)
                train {
                    epochs: 20
                    batch_size: 64
                }
            }
            """,
            "OptimizerModel", (28, 28, 1),
            [
                {'type': 'Dense', 'params': {'units': 64, 'activation': 'relu'}},
                {'type': 'Output', 'params': {'units': 10, 'activation': 'softmax'}}
            ],
            "categorical_crossentropy", {'type': 'SGD', 'params': {'learning_rate': 0.01}}, {'epochs': 20, 'batch_size': 64}
        )
    ],
    ids=["network-optimizer-params"]
)
def test_network_with_optimizer_params(network_parser, transformer, network_string, expected_name, expected_input_shape, expected_layers, expected_loss, expected_optimizer, expected_training_config):
    tree = network_parser.parse(network_string)
    result = transformer.transform(tree)
    assert result['type'] == 'model'
    assert result['name'] == expected_name
    assert result['input'] == {'type': 'Input', 'shape': expected_input_shape}
    assert result['layers'] == expected_layers
    assert result['loss'] == expected_loss
    assert result['optimizer'] == expected_optimizer
    assert result['training_config'] == expected_training_config