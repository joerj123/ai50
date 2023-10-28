import itertools
import random

printon = False

class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        
        # If count == length of cells (and count is not zero) then all of them must be mines.
        if self.count == len(self.cells) and self.count != 0:
            return self.cells
        
        # TO DO: Do I need to 

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """

        # If count = 0, all of them are safe
        if self.count == 0:
            return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """

        # If the cell is in self.cells
        if cell in self.cells:

            # Reduce the mine count by 1 as we know it's a mine
            if self.count <1:
                raise Exception("Tried to reduce mine count for ", cell,"  in ", self.cells, "but count is ", self.count, "so this doesn't make any sense.")
            self.count -=1

            # Remove the cell from the sentence
            self.cells.remove(cell)

        return(self)

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that a cell is known to be safe.
        """

        # If the cell is in self.cells
        if cell in self.cells:

            # Remove the cell from the sentence
            self.cells.remove(cell)
        
        return(self)

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        
        self.mines.add(cell)
        for sentence in self.knowledge:
            if printon:
                ("I'm marking this cell: ", cell, "as a mine in this sentence: ", sentence)
            sentence.mark_mine(cell)
        #TO DO: Is there a way to mark this visually on the board with the flags?

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge sentences to mark that cell as safe as well.
        """
        self.safes.add(cell)
        if printon:
            ("marked this cell as safe: ", cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)
        #TO DO: Is there a way to mark this visually?


    def add_knowledge(self, cell, count):
        """
        Called by Runner.py when the Minesweeper board tells us, for a given safe cell, how many neighboring cells have mines in them.
        This is called when it has made a move and it's not a mine.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe, updating any sentences that contain the cell as well.
            3) add a new sentence to the AI's knowledge base based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base if they can be inferred from existing knowledge
        """
        
        # 1. Add the move to the list of moves made
        self.moves_made.add(cell)

        # 2. Mark it as safe, updating any sentences that contain the cell
        self.mark_safe(cell)

        """ 
        3. For an i,j tuple, draw all the cells around that cell - taking into account edges of the range.
        Add each surrounding cell to the sentence.
        Update the count for the sentence to the number of mines surrounding it.
        """

        # Initiate a set to get the cells            
        available_cells = set()

        # Get the position of the cell
        i = cell[0]
        j = cell[1]

        # Make a 3 x 3 grid around the cell.
        for a in range(3):
            for b in range(3):

                # The y axis is minus 1, 0 and + 1 around i
                y = a - 1 + i

                # The x axis is minus 1, 0 and + 1 around j
                x = b - 1 + j

                # If not out of range AND not i, j (the cell in question), add it as a tuple to available_cells
                if y >= 0 and y < 8 and x >= 0 and x < 8 and (y, x) != (i, j):
                    t = (y, x)

                    # If this cell is a mine, reduce count by 1 and ignore it
                    if t in self.mines:
                        count = count - 1
                        continue
                    
                    # Checks if this cell is already marked as safe, and if not adds it to knowledge:
                    if t not in self.safes:
                        available_cells.add(t)

        # Initialise new knowledge as a sentence
        new_knowledge = Sentence(available_cells, count)

        # Add to the AI's knowledge. Self is used because by convention, objects used by classes are passed as the first argument to methods in a class.
        if len(new_knowledge.cells) != 0:
            self.knowledge.append(new_knowledge)
            if printon:
                print("Because of move :", cell, "we added new knowledge: ", new_knowledge)

        """
        TO DO
        Any time you have 2 sentences and 1 is a subset of the other, you can subtract set 1 from set 2 and count 1 from count 2.
        So...
        Iterate over all previous sentences...
        Check if this sentence is a subset of another.
        Do the subtraction.
        Add this sentence.

        for sentence in sentences:
            for cell in sentence:
                is this cell in the new knowledge?
                    add to matches
            does length of matches now match length of cells in new knowledge? And is length of matches < length of sentence cells? If true:
                initialise inferred_knowledge
                new_count = sentence count - new knowledge count
                for cell in sentence:
                    if cell not in new knowledge:
                        add to inferred_knowledge.
            add inferred knowledge using add_knowledge
            """

        #Keep looping while knowledge has changed. So set this to true first
        knowledge_updated = True

        while knowledge_updated :

            # Set updated as False to stop the loop next time
            knowledge_updated = False

            # Loop over all the sentences in the Minesweeper AI knowledge base
            if printon:
                print("Now looping over all sentences in the KB")

            for sentence in self.knowledge:

                # Remove empty sentences from the KB
                if sentence.count == 0 and len(sentence.cells) ==0:
                    if printon:
                        print("removed this set as it's empty:", sentence)
                    self.knowledge.remove(sentence)

                # Mark all cells as safe if count is zero
                if sentence.count == 0:
                    if printon:
                        print("All these cells are safes, so adding them to safes list")
                    knowledge_updated = True

                    # Copy to avoid iteration error
                    cell_copy = sentence.cells.copy()

                    for cell in cell_copy:
                        self.mark_safe(cell)
                
                # Mark all cells as mines if count is equal to length
                if len(sentence.cells) == sentence.count:
                    if printon:
                        print("All of these cells are mines so marking them as mines")
                    knowledge_updated = True

                    # Copy to avoid iteration error
                    cell_copy = sentence.cells.copy()

                    for cell in cell_copy:
                        self.mark_mine(cell)

                # Skip if it's the same sentence
                if sentence.cells == new_knowledge.cells:
                    continue

                if printon:
                    print("Checking this sentence:", sentence)
                
                # Initiate a set of matches
                matches = set()

                # Loop over the cells in the current sentence
                for cell in sentence.cells:
                    
                    # Add any cell in the new knowledge that matches the cells in this existing sentence
                    if cell in new_knowledge.cells:
                        matches.add(cell)
                
                # Print all the matches
                if printon  and len(matches) > 0:
                    print("Matches are", matches)
                    

                # If every cell matches a cell from the sentence... and there are fewer cells in matches vs the sentence and there is at least 1 match...
                if len(matches) > 0 and len(matches) == len(new_knowledge.cells) and len(matches) < len(sentence.cells):
                    
                    if printon:
                        print("We have some inferred knowledge here")

                    # Initialise set for tuples
                    s = set()
                    c = 0

                    # Initialise inferred knowledge and put the new inferred count in.
                    inferred_knowledge = Sentence(s, c)

                    # Calculate new count
                    c = sentence.count - new_knowledge.count

                    if inferred_knowledge in self.knowledge:
                        raise Exception("Inferred knowledge is already in the KB")

                    if c < 0:
                        raise Exception("Inferred knowledge count is negative")

                    if printon:
                        print("Sentence count = ", sentence.count, ". New knowledge count = ", new_knowledge.count)

                    if printon:
                        print("New count is ", c)
                    
                    # Add the count to the inferred knowledge
                    inferred_knowledge.count = c

                    # Loop over the current sentence and only add cells if they're not in the new_knowledge cells
                    for cell in sentence.cells:
                        if cell not in new_knowledge.cells:
                            inferred_knowledge.cells.add(cell)
                    
                    # Add the inferred knowledge to the knowledget set IF it's not already in self.knowledge.
                    if inferred_knowledge not in self.knowledge:
                        self.knowledge.append(inferred_knowledge)
                        if printon:
                            print("Added inferred knowledge sentence: ", inferred_knowledge)

                        # Set knowledge updated to True, so we can loop again.
                        knowledge_updated = True
                

        # Print the safes
        if printon:
            print("Safes are ", self.safes)


        # Print the mines
        if printon:
            print("Mines are ", self.mines)


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        # Randomly select a move from 'safes' if that move is not already a made move.

        # Check if safes has some cells in it
        if len(self.safes) > 0:

            # Iterate over safes to check if it hasn't been made already
            for cell in self.safes:
                if cell not in self.moves_made:
                    return cell
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
            3) Return None if there are no moves left.
        """

        possible_moves = set()

        # Iterate over the board
        for y in range(self.height):
            for x in range(self.width):
                cell = (y, x)
                if cell in self.mines:
                    continue
                if cell in self.moves_made:
                    continue
                else:
                    possible_moves.add(cell)
        
        # Return none possible if none
        if len(possible_moves) == 0:
            return None
        
        # Otherwise return a random move from possible moves
        else:
            return(random.choice(list(possible_moves)))
