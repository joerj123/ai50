import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]

def count_genes(person, one_gene, two_genes):

    # Return a variable counting the number of genes
    genes = 1 if person in one_gene else 2 if person in two_genes else 0
    return genes

def trait_bool(person, have_trait):

    # Return a boolean stating whether someone has the trait
    trait = True if person in have_trait else False
    return trait

def transmit_prob(child_genes, m_genes, f_genes):

    # Get generic probabilities
    p_no_mutation = (1 - PROBS["mutation"])
    p_mutation = PROBS["mutation"]

    # Initiate var
    p = 0

    # Generic probability of passing down 1 gene from parent
    p_parent_transmit = {
        0 : p_mutation,
        1 : (0.5 * p_no_mutation) + (0.5 * p_mutation),
        2 : p_no_mutation
    }

    # If child genes are zero, its 1 - prob of passing down 1 gene (f) * (1 - prob of passing down a gene (m))
    if child_genes == 0:
        p = (1 - p_parent_transmit[m_genes]) * (1 - p_parent_transmit[f_genes])

    # If child genes are 1, it's:
        # prob of passing down gene (f) * (1 - prob of passing down gene (m)) +
        # prob of passing down gene (m) * (1 - prob of passing down gene (f))
    elif child_genes == 1:
        p = (p_parent_transmit[m_genes]) * (1 - p_parent_transmit[f_genes]) + (p_parent_transmit[f_genes] * (1 - p_parent_transmit[m_genes]))
    
    # if child genes are 2 it's prob of passing down gene (f) * prob of passing down gene (m)
    elif child_genes == 2:
        p = p_parent_transmit[m_genes] * p_parent_transmit[f_genes]

    return p

def joint_probability(people, one_gene, two_genes, have_trait):

    # Create a set of names, people with no genes and people with no trait
    names = set()
    no_genes = set()
    no_trait = set()
    for person in list(people.keys()):
        names.add(person)
        if person not in one_gene and person not in two_genes: no_genes.add(person)
        if person not in have_trait: no_trait.add(person)

    # Probability for all people
    joint_prob = 1

    # Loop over the people
    for person in names:

        # Probability for this person
        p = 1

        # Put the genetic info for this person in variables
        m = people[person]["mother"]
        f = people[person]["father"]
        parents = 0 if m == None and f == None else 1
        genes = count_genes(person, one_gene, two_genes)
        trait = trait_bool(person, have_trait)

        # Create generic probabilities
        p_no_mutation = 1 - PROBS["mutation"]

        # If no parents, use generic probability based on genes (we'll trait-weight later)
        if parents == 0:
            p *= PROBS["gene"][genes]
        
        else:        
            # Call the transmission probabilities function
            p *= transmit_prob(genes, count_genes(m, one_gene, two_genes), count_genes(f, one_gene, two_genes))

        # Calc trait-weighted probability
        p *= PROBS["trait"][genes][trait]

        # Update the joint probability for this person
        joint_prob = joint_prob * p

    # Quit
    # sys.exit()
    
    return joint_prob

def update(probabilities, one_gene, two_genes, have_trait, p):

    # Loop over the people in the dictionary.   
    for person in list(probabilities.keys()):

        # Get genetic info variables and update probabilities
        genes = count_genes(person, one_gene, two_genes)
        trait = trait_bool(person, have_trait)
        probabilities[person]["gene"][genes] += p
        probabilities[person]["trait"][trait] += p

def normalize(probabilities):

    for person in list(probabilities.keys()):
        
        # Get an adjustment factor
        adj_gene = 1 / (probabilities[person]["gene"][0] + probabilities[person]["gene"][1] + probabilities[person]["gene"][2])
        adj_trait = 1 / (probabilities[person]["trait"][True] + probabilities[person]["trait"][False])

        # Update probabilities
        probabilities[person]["gene"][0] *= adj_gene
        probabilities[person]["gene"][1] *= adj_gene
        probabilities[person]["gene"][2] *= adj_gene
        probabilities[person]["trait"][True] *= adj_trait
        probabilities[person]["trait"][False] *= adj_trait

if __name__ == "__main__":
    main()
