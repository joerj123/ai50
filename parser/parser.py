import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | NP VP NP | NP VP NP Conj S | NP VP Conj VP NP | NP VP Conj VP | VP NP | NP VP P NP | NP VP P NP Conj S
NP -> N | AdjP N | N Adv | N P N | Det AdjP N | N P Det AdjP N | N P N | Det N | Det N Adv | Det Adj N | Det N P N
VP -> V | V Adv | V N | V Det AdjP N
AdjP -> Adj Adj | Adj Adj Adj

"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    # TO DO: rename back to parser.py
    
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """

    # Get the list of words
    list_of_words = nltk.tokenize.word_tokenize(sentence)
    lower_list_of_words = []

    # Loop over the words
    for word in list_of_words:
        has_letter = False

        # Loop over the letters
        for letter in word:
            
            # Check there's an alphabetic letter
            if letter.isalpha():
                has_letter = True
        
        # Check there's at least one alphabetic letter in the word
        if has_letter == True:
            
            # Convert to lowercase
            lower_list_of_words.append(word.lower())
    print(lower_list_of_words)
    return lower_list_of_words

def contains_np(tree):

    # Check if subtrees contain the N label
    for subtree in tree.subtrees():
        if subtree == tree:
            continue
        if subtree.label() == "NP":
            return True
    
    else:
        return False

def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """

    noun_phrase_chunks = []

    # iterate over the subtrees
    for subtree in tree.subtrees():

        # If it contains NP, check if subtrees do to
        if subtree.label() == "NP":
            if contains_np(subtree):
                continue

            # If they do, add to the list
            else:
                noun_phrase_chunks.append(subtree)

    return noun_phrase_chunks

if __name__ == "__main__":
    main()
