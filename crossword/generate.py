import sys
from operator import itemgetter, attrgetter

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # Loop over the variables, removing words that don't match the length of the word
        words_to_remove = []
        for var in self.domains:
            for word in self.domains[var]:
                if len(word) != var.length:
                    words_to_remove.append((var, word))
    
        # Remove the words
        for var, word in words_to_remove:
            self.domains[var].remove(word)
        
        #raise NotImplementedError

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        # Loop over words in x's domain, removing any that are not consistent with y's domain given the arc.
        words_to_remove = []
        for wordx in self.domains[x]:
            is_match = False
            for wordy in self.domains[y]:
                # if the ith character of x's word === the jth character of y's word, set match to True
                if wordx[self.crossword.overlaps[x, y][0]] == wordy[self.crossword.overlaps[x, y][1]]:
                    is_match = True
            if is_match == False:
                words_to_remove.append(wordx)

        # Remove the words
        for word in words_to_remove:
            self.domains[x].remove(word)
            
        # Return true if words were removed otherwise false
        if words_to_remove: return True 
        else: return False

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        # Create a queue
        if arcs is None:
            arcs = self.crossword.overlaps.items()

        # Loop until no changes are made
        change_tracker = True
        while change_tracker:
            change_tracker = False
            for key, value in arcs:
                    # If no overlap in pair, move to the next pair
                    if value is None:
                        continue
                    else:
                        # Call revise, and loop round again if there was a revision
                        if self.revise(key[0], key[1]):
                            change_tracker = True

        # Return false if enforced but some empty domains.
        for var in self.domains:
            if self.domains[var] is None:
                return False

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        2
        """

        # If domain values length is same as assignment values length
        if len(self.domains.values()) == len(assignment.values()):
            if None not in assignment.values():
                return True
        else:
            return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # Check length is correct
        for var in assignment:
            if len(assignment[var]) != var.length:
                return False
            
            # Get neighbours and loop over them
            neighbours = self.neighbours(var)
            for n in neighbours:
                
                # If neighbour has an assignment, check if the intersecting letters match
                if n[1] in assignment:

                    # If overlaps don't match, return false
                    if not self.check_letter_overlaps(n[0], n[1], assignment[n[0]], assignment[n[1]]):
                        return False
                    
        # Check if values are unique
        if len(assignment.values()) != len(set(assignment.values())):
            return False
        
        return True

    def neighbours(self, varx):
        """
        Returns a dict of variables and intersection points for a particular variable. 
        Returns None if no intersections
        """

        neighbours = {}
        for pair in self.crossword.overlaps:
            if varx == pair[1]:
                continue
            if self.crossword.overlaps[varx, pair[1]]:
                neighbours[varx, pair[1]] = self.crossword.overlaps[varx, pair[1]]
        
        if len(neighbours) == 0:
            return None

        else:
            return neighbours

    def check_letter_overlaps(self, varx, vary, wordx, wordy):
        """
        Checks two variables and two words to see if the letters overlap
        """

        # Get the intersection of the vars using overlaps
        intersection = self.crossword.overlaps[varx, vary]

        if wordx[intersection[0]] == wordy[intersection[1]]:
            return True
        else:
            return False
    
    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        # Initialise a dict. This will contain words and number of words they rule out
        words_with_ruledout_count = {}

        # Loop over the words in the domain for this variable
        for wordx in self.domains[var]:

            # Loop over all other variables to find those that overlap
            for vary in self.domains:

                # Check those that do overlap, while skipping overlapping vars
                if var == vary:
                    continue

                if self.crossword.overlaps[var, vary]:
                    
                    # Add if not already in dict
                    if wordx not in words_with_ruledout_count:
                        words_with_ruledout_count[wordx] = 0

                    # Loop over the domain of the neighbour
                    for wordy in self.domains[vary]:

                        # If no overlap, increment the counter
                        if not self.check_letter_overlaps(var, vary, wordx, wordy):
                            words_with_ruledout_count[wordx] += 1

        # Use sorted to sort by count        
        words_with_ruledout_count = sorted(words_with_ruledout_count.items(), key=lambda count: count[1])

        # Return as a list using list compression
        words = [t[0] for t in words_with_ruledout_count]
        return words

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        # Make a list for the tuples
        remaining_vars = []

        # Loop over domains to find unassigned variables
        for var in self.domains:
            if var not in assignment:
                words_count = len(self.domains[var])
                neighbour_count = len(self.neighbours(var))

                # Add a tuple with the var and the counts
                remaining_vars.append((var, words_count, neighbour_count))
        
        # Sort by word cound, then neighbour count
        remaining_vars = sorted(remaining_vars, key=itemgetter(1,2))

        # Return the var from the 1st item in the list
        return remaining_vars[0][0]
        

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        if self.assignment_complete(assignment):
            return assignment
            
        # Pick a variable that hasn't been assigned (use select unassigned variable)
        var = self.select_unassigned_variable(assignment)
        
        # Get a list of words in that variable's domain (use order domain values)
        words = self.order_domain_values(var, assignment)
        
        # Loop over the words
        for word in words:

            # Add the word to the temp_assignment and check if it's consistent
            assignment[var] = word
            if self.consistent(assignment):
                
                # Call backtrack with this new assignment.
                result = self.backtrack(assignment)

                if result is not None:
                # If result is not a failure, return the result (because it's recursive result will always be complete)
                    return result
                    
            del assignment[var]
        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
