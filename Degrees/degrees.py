import csv
import sys
import time # Might need to REMOVE THIS!

from util import Node, StackFrontier, QueueFrontier, Visited

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):

    # print("Hello world. Source is ", source," . And Target is ", target)

    """Keep track of number of states explored"""

    num_states_explored = 0

    """"Initialize the frontier to the starting state. State is where it's pointed at now."""

    start = Node(state=source, parent=None, action=None)
    frontier = QueueFrontier()
    frontier.add(start)

    """Find the initial frontier"""

    current_node = start

    """Create a list of visited nodes"""

    visited_nodes = Visited()

    """Create a loop until there is no frontier left"""

    while not frontier.empty(): # Checks is the frontier is empty

        # print("Current node state before we remove use .remove to take it from the frontier:", current_node.state)

        current_node = frontier.remove() # CHANGE the node. It moves the node to the last one in the frontier.

        if not visited_nodes.contains_state(current_node.state):

            # print("Removed node from the frontier - this is now the current_node:", current_node.state)

            """If the node we're considering matches the solution, return the path"""
            if current_node.state == target:
                path = [] # Square brackets denotes a list. In the list are tuples in the format (movie, person) with their IDs
                temp_node = current_node
                # Get the path by following the parent.
                # print("We found a solution by following ", num_states_explored, " states, so we're returning the Path now.")
                while temp_node.parent is not None:
                    path.append((temp_node.action, temp_node.state))
                    # print("Added movie -", temp_node.state," of type ", type(temp_node.state), " - and person - ", temp_node.action," of type ", type(temp_node.action), " to path")
                    """Point the temp node to the last visited node in the path"""
                    temp_node = visited_nodes.get_node_by_state(temp_node.parent)

                path.reverse() #Reverse the order of the path so it displays the path in order

                return path

            else:
                """The current node is not the target, so we're going to add the neighbours"""

                visited_nodes.add(current_node) #Add the node to the list of visited nodes

                num_states_explored+=1 # Adds to the counter of the number of states explored

                current_node_neighbours = neighbors_for_person(current_node.state) #Get the neighbours for the current node.

                for element in current_node_neighbours:
                    temp_node = Node(state=element[1], parent=current_node.state, action=element[0]) # Make a temp node with the neighbours list. Parent is the current node state.
                    frontier.add(temp_node) #Add each temp node to the frontier
                    # print("Node  added to frontier: state, parent, action: ", temp_node.state, temp_node.parent, temp_node.action)

                # time.sleep(0.5) #Pause for a sec            

    """If neighbours of current node == zero, return no solution."""
    return None

def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
