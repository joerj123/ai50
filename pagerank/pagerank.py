import os
import random
import re
import sys
from copy import deepcopy

DAMPING = 0.85
SAMPLES = 10000

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):

    # Initialise the test counter and dict to be returned.
    test_counter = 0
    distribution = {}

    # If page has no outgoing links, then transition_model should return a probability distribution that chooses randomly among all pages with equal probability. (In other words, if a page has no links, we can pretend it has links to all pages in the corpus, including itself.)

    if len(corpus[page]) == 0:
        for p in corpus:
            distribution[p] = 1 / len(corpus)
            test_counter += 1 / len(corpus)
    else:
    
        # Create the 'random move probability'
        random_probability = (1 - damping_factor) / len(corpus)

        # Create the 'linked move probability'
        linked_probability = damping_factor / len(corpus[page])


        # Construct the dictionary to be returned
        for p in corpus:
            if p in corpus[page]:
                distribution[p] = random_probability + linked_probability
                test_counter += random_probability + linked_probability
            else:
                distribution[p] = random_probability
                test_counter += random_probability

    # test that the sum of the items in the dict = 1, otherwise raise an exception
    if test_counter >= 1.00000001 or test_counter <= 0.999999999:
        raise Exception("Error: The distribution doesn't equal 1")

    return distribution


def sample_pagerank(corpus, damping_factor, n):

    # Make the empty dict for samples.
    count_dict = {}
    for p in corpus:
        count_dict[p] = 0
    
    # Keep track of the last page
    selected_page = ""

    # Loop n times to sample pages.
    i = 0
    while i < n:

        # For the first sample, select one at random
        if i == 0:
            selected_page = random.choice(list(count_dict.keys()))
        
        else:
            # Pick the next page using the probability distributon
            transitions = transition_model(corpus, selected_page, damping_factor)
            selected_page = random.choices(list(transitions.keys()), list(transitions.values()), k=1)[0]

        # Otherwise, increment the counter and add the sample
        i+=1
        count_dict[selected_page] += 1

    # Change absolute values into percentages + test that the sum of the items in the dict = 1, otherwise raise an exception
    test_counter = 0
    for p in count_dict:
        count_dict[p] = count_dict[p] / n
        test_counter += count_dict[p]
            
    if test_counter >= 1.00000001 or test_counter <= 0.999999999:
        raise Exception("Error: The distribution doesn't equal 1")

    return count_dict


def iterate_pagerank(corpus, damping_factor):

    # Get size of corpus
    corpus_size = len(list(corpus.keys()))

    # Initiate the pagerank megadict
    pagerank = {}
    for p in corpus:
        pagerank[p] = {
            "pagerank" : 1 / corpus_size,
            "numlinks" : len(corpus[p]) # count the number of links on this page
        }
        # A page that has no links at all should be interpreted as having one link for every page in the corpus (including itself).
        if pagerank[p]["numlinks"] == 0: 
            pagerank[p]["numlinks"] = corpus_size # Update the link count to match number of pages in corpus
            corpus[p] = list(corpus.keys()) # Add the links to the corpus
        pagerank[p]["weightedPR"] = pagerank[p]["pagerank"] / pagerank[p]["numlinks"] # calc weighted pagerank

    # Create LinksTo table
    linksto = {}
    for p in corpus: # populate for each of the megadict rows
        linksto[p] = [] # create a row in the linksto table with an empty list.
        for c in corpus: # loop over the corpus to get links pointing to this page
            if p in corpus[c]: # check each link to see if it is pointing to p.
                linksto[p].append(c) # add c to the list of inbound links

    # Run the while loop to adjust pageranks based on links to this page
    new_pr = {} # Make a temporary dictionary with new ranks.
    tolerance = 0.001

    while True:
        for p in pagerank:
            random_chance = (1 - damping_factor) / corpus_size
            linked_chance = 0
            total_chance = 0
            for l in linksto[p]:
                # print("linksto[p]:", linksto[p], "l: ", l)
                linked_chance += pagerank[l]["weightedPR"] # sum the weighted pageranks

            total_chance = random_chance + (damping_factor * linked_chance) # get the total chance inc. weighting the linked chance by d
            #  print(p, "random_chance:", random_chance, "linked_chance:", linked_chance, "old PR:", pagerank[p]["pagerank"], "new PR:", total_chance)
            
            # create a dict within the new_pr dict with temp values
            new_pr[p] = {
                "pagerank" : total_chance,
                "numlinks" : pagerank[p]["numlinks"],
                "weightedPR" : total_chance / pagerank[p]["numlinks"]
            }

        # Loop over new PR vs old PR. If abs of any diff >= tolerance, do another iteration
        continue_flag = False
        for p in new_pr:
            diff = abs(new_pr[p]["pagerank"] - pagerank[p]["pagerank"])
            # print(p, "old PR:",pagerank[p]["pagerank"], "new PR:", new_pr[p]["pagerank"], "diff:", diff)
            if diff >= tolerance:
                continue_flag = True
        
        # Update the megadict
        pagerank = deepcopy(new_pr)

        # If none of the diffs were greater than or equal to the tolerance, break the loop
        if continue_flag == False:
            break

    """Construct the return dict"""
    test_counter = 0
    pagerank_return = {}
    for p in pagerank:
        pagerank_return[p] = pagerank[p]["pagerank"]
        test_counter += pagerank[p]["pagerank"]
    
    # test that the sum of the items in the dict = 1, otherwise raise an exception
    if test_counter >= 1.00000001 or test_counter <= 0.999999999:
        raise Exception(f"Error: The distribution doesn't equal 1. It equals {test_counter}.")
    
    return pagerank_return

if __name__ == "__main__":
    main()
