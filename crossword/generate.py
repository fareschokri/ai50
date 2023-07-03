import copy
import sys

from crossword import *
from operator import itemgetter


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
                        w, h = draw.textsize(letters[i][j], font=font)
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
        for var in self.domains:
            for val in copy.copy(self.domains[var]):
                if len(val) != var.length:
                    self.domains[var].remove(val)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        if (x, y) in self.crossword.overlaps and self.crossword.overlaps[(x, y)] is not None:

            copy_domain = copy.copy(self.domains[x])
            for x_val in copy_domain:
                no_match = True
                for y_val in self.domains[y]:
                    overlap = self.crossword.overlaps[(x, y)]
                    if len(x_val) > overlap[0] and len(y_val) > overlap[1] and x_val[overlap[0]] == y_val[overlap[1]]:
                        no_match = False
                if no_match:
                    self.domains[x].remove(x_val)
            if len(copy_domain) != len(self.domains[x]):
                return True
        return False

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        if arcs is None:
            queue = copy.copy(self.crossword.overlaps)
        else:
            queue = arcs
        while len(queue) > 0:
            couple = queue.popitem()
            if self.revise(couple[0][0], couple[0][1]):
                if len(self.domains[couple[0][0]]) == 0:
                    return False
                for other_var in self.crossword.overlaps:
                    if couple[0][0] in other_var and couple[0][1] not in other_var and other_var not in queue:
                        queue[other_var] = self.crossword.overlaps[other_var]
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(assignment) == len(self.crossword.variables):
            for var in assignment:
                if len(assignment[var]) != 1:
                    return False
            return True
        return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for var in assignment:
            for val in list(assignment[var]):
                if len(val) != var.length:
                    return False
                for next_var in assignment:
                    if var != next_var and val in assignment[next_var]:
                        return False
                    if var != next_var and next_var in self.crossword.neighbors(var):
                        for next_val in list(assignment[next_var]):
                            overlap = self.crossword.overlaps[(var, next_var)]
                            if overlap is not None and val != next_val and len(val) > overlap[0] and len(next_val) > overlap[1] and val[overlap[0]] != next_val[overlap[1]]:
                                return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        val_weights = []
        for val in self.domains[var]:
            if self.consistent({var: [val]}):
                val_weight = 0
                for next_var in self.domains:
                    if var != next_var and next_var not in assignment and next_var in self.crossword.neighbors(var):
                        overlap = self.crossword.overlaps[(var, next_var)]
                        for next_val in self.domains[next_var]:
                            if val == next_val:
                                val_weight += 1
                            elif overlap is not None and val[overlap[0]] != next_val[overlap[1]]:
                                val_weight += 1
                val_weights.append((val, val_weight))
        final_list = []
        for (x, y) in sorted(val_weights, key=itemgetter(1)):
            final_list.append(x)
        return final_list

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        vars_domains = []
        for var in self.domains:
            if var not in assignment:
                vars_domains.append((var, len(self.domains[var]), len(self.crossword.neighbors(var))))
        vars_domains = sorted(vars_domains, key=itemgetter(1))
        if len(vars_domains) > 1 and vars_domains[0][1] == vars_domains[1][1]:
            vars_domains = sorted(vars_domains, key=itemgetter(2), reverse=True)
        return vars_domains[0][0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            for var in assignment:
                assignment[var] = assignment[var][0]
            return assignment
        var = self.select_unassigned_variable(assignment)
        actual_var = Variable(var.i, var.j, var.direction , var.length).__repr__()
        for value in self.order_domain_values(var, assignment):
            temp_assignment = copy.copy(assignment)
            temp_assignment[var] = [value]
            if self.consistent(temp_assignment):
                assignment[var] = [value]
                arcs = dict()
                for other_var in self.crossword.neighbors(var):
                    if self.crossword.overlaps[var, other_var] is not None:
                        arcs[var, other_var] = self.crossword.overlaps[var, other_var]
                self.ac3(arcs)
                result = self.backtrack(assignment)
                if result is not None:
                    return result
                else:
                    assignment.pop(var)
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
