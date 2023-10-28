import cv2
import numpy as np
import os
import sys
import tensorflow as tf

from sklearn.model_selection import train_test_split

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    model.evaluate(x_test,  y_test, verbose=2)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """

    # Declare the list that will contain the images
    images = []

    # Declare the labels that will be contained within it.
    labels = []

    # Loop through each category folder
    for x in range(NUM_CATEGORIES):

        # Get the folder path using data_dir
        folderpath = os.path.join(data_dir,str(x))

        # Sub-loop through each image in each category
        for filename in os.listdir(folderpath):

            file_path = os.path.join(folderpath, filename)
            
            # Use Use the OpenCV-Python module (cv2) to read each image
            img_cv2 = cv2.imread(file_path)

            # Format each image as a numpy ndarray with dimensions 30 x 30 x 3.
            resized = cv2.resize(img_cv2, (30, 30))

            # Test the image was read correctly
            assert img_cv2 is not None, "Error: couldn't read the file"

            # Create the numpy image
            numpy_img = np.array(resized)

            # Pass the numpy ndarray and label (integer) to their respective lists.
            images.append(numpy_img)
            labels.append(int(x))
        
        print("added images from this folder", folderpath)

    output_tuple = (images, labels)
    return output_tuple

def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """

    # Create a sequential neural network
    model = tf.keras.models.Sequential([

        # Convolutional layer. Learn 32 filters using a 3x3 kernel
        tf.keras.layers.Conv2D(
            32, (3, 3), activation="relu", input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)
        ),

        # Max-pooling layer, using 2x2 pool size
        # Looks at 2x2 regions and extracts the maximum value. Reduces size of input.
        tf.keras.layers.MaxPooling2D(pool_size=(2,2)),

        # Convolutional layer. Learn 32 filters using a 3x3 kernel
        tf.keras.layers.Conv2D(
            32, (3, 3), activation="relu"
        ),

        # Flatten units into a single layer, enabling them to be processed by the hidden layer
        tf.keras.layers.Flatten(),

        # Add a hidden layer with dropout
        tf.keras.layers.Dense(128, activation="relu"),
        tf.keras.layers.Dropout(0.3),

        # Add an output layer with output units
        tf.keras.layers.Dense(NUM_CATEGORIES, activation="softmax")
    ])

    # Train the neural net
    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    # Return the compiled convolutional neural net
    return model


if __name__ == "__main__":
    main()
