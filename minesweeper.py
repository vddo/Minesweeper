import itertools
import random
import copy


class Minesweeper():
    """
    Minesweeper game representation
    - Generates map with randomly placed mines. Returns amount of mines
    - that border the played move.
    - Checks winning condition.
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
                row.append(False)   # Fills rows and columns with "False"
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))      # self.mines stores coordinates
                self.board[i][j] = True     # self.board (list) marks as True

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
        for i in range(cell[0] - 1, cell[0] + 2):           # Ignoring boarders
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue                # Skipps in looping

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:    # Checking because boarders were ignored
                    if self.board[i][j]:    # If i,j is True
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
        self.mines = set()
        self.safes = set()

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        return self.mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        return self.safes

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.mines.add(cell)
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.safes.add(cell)
            self.cells.remove(cell)


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

        # Set of all possible moves/cells
        self.all_moves = set(itertools.product(
            range(self.height), range(self.width), repeat=1))

        self.ghost_cells = set(itertools.product(
            range(-1, self.height+1), range(-1, self.width+1), repeat=1))
        self.ghost_cells.difference_update(self.all_moves)

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # Accept cell as tuple(i,j)
        # 1)
        self.moves_made.add(cell)

        # 2)
        self.safes.add(cell)

        # 3)
        # Define set of neighboring cells
        i, j = cell
        neighbors = set(itertools.product(
            range(i-1, i+2), range(j-1, j+2), repeat=1))
        neighbors.remove(cell)
        neighbors.difference_update(self.ghost_cells)

        # Update knowledge with new sentence
        new_sentence = Sentence(cells=neighbors, count=count)
        self.knowledge.append(new_sentence)

        # Update knowledge
        # Mark known safes or mines
        # Mark safes
        for sentence in self.knowledge:
            if sentence.count == 0:
                to_mark_safe = copy.deepcopy(sentence.cells)
                for safe_cell in to_mark_safe:
                    self.mark_safe(safe_cell)
        # Update knowledge with mines
        # Mark mines: if len(neighbors) == count then all neighbors mines
            if len(sentence.cells) == sentence.count:
                to_mark_mine = copy.deepcopy(sentence.cells)
                for found_mine in to_mark_mine:
                    self.mark_mine(found_mine)

        # Update knowledge_base
        # for each element in knowledge (sentences)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # Compare self.safes with self.moves_made
        # Cells that are in self.safes but not in self.moves_made can be chosen
        # for next safe move

        # First check if self.safes is superset of self.moves_made
        # Then subtract the same elements from both sets maves_made and safes
        print("mines:", self.mines)
        print("safes:", self.safes)
        if self.safes.issuperset(self.moves_made):
            pot_safe_moves = self.safes.difference(self.moves_made)
        else:
            raise Exception("moves_made not subset of safes")
        if len(pot_safe_moves) == 0:
            return None
        else:
            return pot_safe_moves.pop()

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        print("mines:", self.mines)
        print("safes:", self.safes)
        # Merge self.moves_made and self.mines
        no_moves = self.mines.union(self.moves_made)

        # Subtract no_moves from self.all_moves
        pot_rand_moves = self.all_moves.difference(no_moves)

        return pot_rand_moves.pop()
