import csv
import sys

from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")

def to_month(month_string):

    # Try both shortened and full-length month formats to return the month
    for format in ('%b', '%B'):
        try:
            return datetime.strptime(month_string, format).month
        except:
            continue
    raise Exception("Could not create a valid date from input data", month_string)

def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """

    # Initiate evidence list of lists & labels list
    evidence = []
    labels = []

    # Open the CSV into a dict
    with open (filename, 'r') as f:
        d = csv.DictReader(f)
        for row in d:
            # Create an evidence list with each of the values in the correct format
            l = []
            l.append(int(row["Administrative"]))
            l.append(float(row["Administrative_Duration"]))
            l.append(int(row["Informational"]))
            l.append(float(row["Informational_Duration"]))
            l.append(int(row["ProductRelated"]))
            l.append(float(row["ProductRelated_Duration"]))
            l.append(float(row["BounceRates"]))
            l.append(float(row["ExitRates"]))
            l.append(float(row["PageValues"]))
            l.append(float(row["SpecialDay"]))
            l.append(int(to_month(row["Month"])))
            l.append(int(row["OperatingSystems"]))
            l.append(int(row["Browser"]))
            l.append(int(row["Region"]))
            l.append(int(row["TrafficType"]))
            l.append(int(1 if row["VisitorType"] == "Returning_Visitor" else 0))
            l.append(int(1 if row["Weekend"] == "TRUE" else 0))

            # Append that list to the list of lists
            evidence.append(l)

            # Add the revenue label to labels
            if row["Revenue"] == "TRUE":
                labels.append(1)
            else:
                labels.append(0)

    t = (evidence, labels)
    return t


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """

    true_count = 0
    false_count = 0
    true_correct = 0
    false_correct = 0
    actual_count = len(labels)

    # Loop over the labels and predictions using zip (iterator over 2 lists at the same time)
    for actual, predicted in zip(labels, predictions):
        if actual == 1:
            true_count += 1
            if predicted == 1:
                true_correct += 1
        if actual == 0:
            false_count +=1
            if predicted == 0:
                false_correct += 1

    print(true_correct)
    print(false_correct)

    sensitivity = float(true_correct / true_count)
    specificity = float(false_correct / false_count)
    t = (sensitivity, specificity)
    return t

if __name__ == "__main__":
    main()
