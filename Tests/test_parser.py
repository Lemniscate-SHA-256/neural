import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from parser import propagate_shape, parser, ModelTransformer


def test_parser():
    code = """
    network MyModel {
        input: (28, 28, 1)
        layers:
            Conv2D(filters=32, kernel_size=(3, 3), activation="relu")
            MaxPooling2D(pool_size=(2, 2))
            Flatten()
            Dense(units=128, activation="relu")
            Output(units=10, activation="softmax")
        loss: "categorical_crossentropy"
        optimizer: "adam"
    }
    """
    tree = parser.parse(code)
    transformer = ModelTransformer()
    model_data = transformer.transform(tree)
    assert model_data["name"] == "MyModel"
    assert model_data["input"]["shape"] == (28, 28, 1)
    assert len(model_data["layers"]) == 4