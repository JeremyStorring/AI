"""
Jeremy Storring, JNS855, 11218129
CMPT 317: A4Q4
Michael Horsch
"""

# The Game Class encodes the rules of a game.  
# Game Class Interface:
#    initial_state(self)
#       - returns an initial game state
#       - the state can be any object that stores the details 
#         needed to keep track of the game, including any information
#         convenient to store
#           
#    is_mins_turn(self, state)
#    is_maxs_turn(self, state)
#       - return a boolean that indicates if it's Min/Max's turn
#           
#    is_terminal(self, state)
#       - return a boolean that indicates if the state represents
#         a true end of the game situation, i.e, a win or a draw
#           
#    utility(self, state)
#       - return the utility value of the given terminal state
#       - must return one of three values: k_min, k_draw, k_max
#           k_min: the value returned if Min is the winner
#           k_max: the value returned if Max is the winner
#           k_draw: the value returned if the game ends in a draw
#           - any range is allowed. 
#           - probably best if k_min < k_draw < k_max 
#             and k_draw half way between k_min, k_max
#       - will only be called if the state is determined to be
#         a terminal state by is_terminal()
#       - only terminal states have utility; other states get 
#         their value from searching.
#           
#    actions(self, state)
#       - returns a list of actions legal in the given state
#           
#    result(self, state, action)
#       - returns the state resulting from the action in the given state
#           
#    cutoff_test(self, state, depth)
#       - returns a bolean that indicates if this state and depth is suitable 
#         to limit depth of search.  A simple implementation might just look 
#         at the depth; a more sophisticated implementation might look at 
#         the state as well as the depth.
#           
#    eval(self, state)
#       - returns a numeric value that estimates the minimax value of the
#         given state.  This gets called if cutoff_test() returns true.
#         Instead of searching to the bottom of the tree, this function
#         tries to guess who might win.  The function should return a value 
#         that is in the range defined by utility().  Because this is an
#         estimate, values close to k_min (see utility()) indicate that 
#         a win for Min is likely, and values close to k_max should indicate 
#         a win for Max is likely.  Should not return values outside the range
#         (k_min, k_max).  k_min means "Min wins"; a value smaller than k_min
#         makes no sense.  An estimate from eval() cannot be more extreme than a 
#         fact known from utility().
#           
#    transposition_string(self)
#       - return a string representation of the state
#       - for use in a transposition table
#       - this string should represent the state exactly, but also without
#         too much waste.  In a normal game, lots of these get stored!
#           
#    congratulate(self)
#       - could be called at the end of the game to indicate who wins
#       - this is not absolutely necessary, but could be informative

class GameState(object):
    """ The GameState class stores the information about the state of the game.
        TicTacToe has a 3x3 game board, and players alternately place X or O in
        a blank cell.

        The object has the following attributes:
            self.gameState - a dictionary with
                              keys: (row, col)
                              values: blank, S, R, J
            self.gameSize - the size of the game board to allow checking bounds and where pieces can go
            self.rebels - a list of rebel pieces, each index will be a tuple containing the piece name, and where its
                          current location is
            self.sith - a list of sith pieces, each index will be a tuple containing the piece name, and where its
                          current location is
            self.jedi - a list of jedi pieces, each index will be a tuple containing the piece name, and where its
                          current location is
            self.maxsturn - a boolean value, True if it's Max's turn
                           - storing this makes deciding whose turn it is a bit faster
            self.moveCount - a variable that keeps track of how many moves have been made, 40 is the limit
            self.cachedWin - a boolean value, True if one of the players has won
                           - storing this makes a few calculations a bit faster
            self.cachedWinner - if cachedWin is True, this is a Boolean (True: Win for Max)
                                None if cachedWin is False
                              - stored to make some calculations faster
            self.string - a unique string representation of the gameState
        """

    # make some class-wide constants available for quicker calculations

    _ablank = "  "  # Empty board space
    _anS = "S"  # Sith
    _anR = "R"  # Rebel
    _anJ = "J"  # Jedi

    def __init__(self, size):
        """ Create a new game state object.
        """
        self.gameState = dict()
        self.gameSize = size
        # Create empty lists for game pieces
        self.rebels = []
        self.sith = []
        self.jedi = []
        # Make the board full of empty pieces
        for r in range(0, size):
            for c in range(0, size):
                self.gameState[r, c] = self._ablank
        # Set the top middle piece to be a sith piece
        middle = self.gameSize // 2
        self.gameState[0, middle] = self._anS + str(len(self.sith))
        self.sith.append((self._anS + str(len(self.sith)), 0, middle))
        # Set the bottom row to be rebel pieces
        for i in range(self.gameSize):
            self.gameState[self.gameSize - 1, i] = self._anR + str(len(self.rebels))
            self.rebels.append((self._anR + str(len(self.rebels)), self.gameSize - 1, i))

        self.maxsTurn = True
        self.moveCount = 0
        self.cachedWinner = None
        self.cachedWin = False
        self.string = str(self)

    def myclone(self, size):
        """ Make and return an exact copy of the state.
        """
        newState = GameState(size)
        newState.gameSize = self.gameSize
        newState.rebels = self.rebels.copy()
        newState.sith = self.sith.copy()
        newState.jedi = self.jedi.copy()

        for rc in self.gameState:
            newState.gameState[rc] = self.gameState[rc]

        newState.cachedWinner = self.cachedWinner
        newState.moveCount = self.moveCount
        newState.maxsTurn = self.maxsTurn
        newState.cachedWin = self.cachedWin
        newState.string = str(newState)

        return newState

    def display(self):
        """
        Present the game state to the console.
        """
        for r in range(0, self.gameSize):
            print("+--" * self.gameSize + "+")
            print("|", end="")
            for c in range(0, self.gameSize - 1):
                print(self.gameState[r, c], end="")
                print("|", end="")
            print(self.gameState[r, self.gameSize - 1], end="")
            print("|")
        print("+--" * self.gameSize + "+")

    def __str__(self):
        s = ""
        for r in range(0, self.gameSize):
            for c in range(0, self.gameSize):
                s += self.gameState[r, c]
        return s


class Game(object):
    """ The Game object defines the interface that is used by Game Tree Search
        implementation.
    """

    def __init__(self, size, depth=0):
        """ Initialization.
        """
        self.gameSize = size
        self.depthLimit = depth

    def initial_state(self):
        """ Return an initial state for the game.
        """
        newState = GameState(self.gameSize)
        return newState

    def is_mins_turn(self, state):
        """ Indicate if it's Min's turn
            :return: True if it's Min's turn to play
        """
        state.moveCount += 1
        return not state.maxsTurn

    def is_maxs_turn(self, state):
        """ Indicate if it's Min's turn
            :return: True if it's Max's turn to play
        """
        state.moveCount += 1
        return state.maxsTurn

    def is_terminal(self, state):
        """ Indicate if the game is over.
            :param node: a game state with stored game state
            :return: a boolean indicating if node is terminal
        """
        return state.cachedWin or state.moveCount == 40 or len(state.sith) == 0 or len(state.jedi) + len(
            state.rebels) == 0

    def actions(self, state):
        """ Returns all the legal actions in the given state.
            :param state: a state object
            :return: a list of actions legal in the given state
        """
        if state.maxsTurn:
            # get rebel forces actions (Player 1)
            rebels = self.rebelActions(state)
            jedis = self.jediActions(state)
            allActions = rebels + jedis
        else:
            # Get sith actions (Player 2)
            sith = self.sithActions(state)
            allActions = sith
        return allActions

    def jediActions(self, state):
        """
        Returns all the legal actions for each jedi on the game board
        :param state: a state object
        :return: a list of jedi actions legal in the given state
        """
        actions = []
        # All 8 directions for a jedi to move
        moves = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
        for i in state.jedi:
            for move in moves:
                xtemp, ytemp = i[1] + move[0], i[2] + move[1]
                # check if the movement is valid
                while self.isValid(state, xtemp, ytemp):
                    if state.gameState[xtemp, ytemp] != "  ":
                        if state.gameState[xtemp, ytemp][0] == "S":
                            actions.append((state.maxsTurn, i[0], xtemp, ytemp, i[1], i[2]))
                        break
                    actions.append((state.maxsTurn, i[0], xtemp, ytemp, i[1], i[2]))
                    xtemp, ytemp = xtemp + move[0], ytemp + move[1]
        return actions

    def sithActions(self, state):
        """
        Returns all the legal actions for each sith on the game board
        :param state: a state object
        :return: a list of sith actions legal in the given state
        """
        actions = []
        for i in state.sith:
            for x in range(-1, 2):
                for y in range(-1, 2):
                    xpos = i[1] + x
                    ypos = i[2] + y
                    if self.isValid(state, xpos, ypos):
                        if state.gameState[xpos, ypos][0] != "S":
                            # add all positions around S if it is valid, and is not another sith
                            actions.append((state.maxsTurn, i[0], xpos, ypos, i[1], i[2]))
        # Currently removes positions that would allow a sith to stay in the same spot. This could be simplified.
        toRemove = []
        if len(actions) > 0:
            for i in range(len(actions)):
                if actions[i][2] == actions[i][4] and actions[i][3] == actions[i][5]:
                    toRemove.append(i)
        if len(toRemove) > 0:
            for i in toRemove:
                del actions[i]
        return actions

    def rebelActions(self, state):
        """
        Returns all the legal actions for each jedi on the game board
        :param state: a state object
        :return: a list of jedi actions legal in the given state
        """
        actions = []
        for i in state.rebels:
            if self.isValid(state, i[1] - 1, i[2] + 1):
                # if a sith is up and to the right
                if state.gameState[i[1] - 1, i[2] + 1][0] == "S":
                    actions.append((state.maxsTurn, i[0], i[1] - 1, i[2] + 1, i[1], i[2]))

            if self.isValid(state, i[1] - 1, i[2] - 1):
                # if a sith is up and to the left
                if state.gameState[i[1] - 1, i[2] - 1][0] == "S":
                    actions.append((state.maxsTurn, i[0], i[1] - 1, i[2] - 1, i[1], i[2]))

            if self.isValid(state, i[1] - 1, i[2]):
                # if a forward move that is not blocked
                if state.gameState[i[1] - 1, i[2]][0] != "S" or state.gameState[i[1] - 1, i[2]][0] != "J":
                    actions.append((state.maxsTurn, i[0], i[1] - 1, i[2], i[1], i[2]))

        return actions

    def isValid(self, state, x, y):
        """
        Checks if the given coordinates are inside the game state (a legal move)
        :param state: a game state object
        :param x: the desired x coordinate
        :param y: the desired y coordinate
        :return: True if a valid move, False otherwise
        """
        if x >= 0 and x < state.gameSize and y >= 0 and y < state.gameSize:
            return True
        return False

    def result(self, state, action):
        """ Return the state that results from the application of the
            given action in the given state.
            :param state: a legal game state
            :param action: a legal action in the game state
            :return: a new game state
        """
        newState = state.myclone(state.gameSize)

        if action[0]:
            # if the action is updating a rebel piece
            if action[1][0] == "R":
                newState = self.updateRebels(newState, action)
            else:
                # update jedi piece
                newState = self.updateJedi(newState, action)
        else:
            # update sith piece
            newState = self.updateSith(newState, action)

        newState.maxsTurn = not state.maxsTurn # change turns
        self._cache_winner(action[0], action[2], action[3], newState)
        newState.string = str(newState) # update the state string

        return newState

    def updateJedi(self, state, action):
        """ Return the state that results from the application of the
            given action in the given state.
            :param state: a legal game state
            :param action: a legal action in the game state
            :return: a new game state
        """
        who, piece, x, y, oldX, oldY = action
        if state.gameState[x, y][0] == "S":
            # if the jedi is moving to a spot with a sith
            jediIndex = state.jedi.index((piece, oldX, oldY))
            sithIndex = state.sith.index((state.gameState[x, y], x, y))
            state.gameState[x, y] = piece
            state.jedi[jediIndex] = (piece, x, y)
            state.gameState[oldX, oldY] = "  "
            del state.sith[sithIndex]
        else:
            # if the jedi is moving anywhere else (a blank spot)
            jediIndex = state.jedi.index((piece, oldX, oldY))
            state.gameState[x, y] = piece
            state.jedi[jediIndex] = (piece, x, y)
            state.gameState[oldX, oldY] = "  "
        return state

    def updateSith(self, state, action):
        """ Return the state that results from the application of the
            given action in the given state.
            :param state: a legal game state
            :param action: a legal action in the game state
            :return: a new game state
        """
        who, piece, x, y, oldX, oldY = action
        if state.gameState[x, y] == "  ":
            # if the sith is moving to an empty spot
            sithIndex = state.sith.index((piece, oldX, oldY))
            state.gameState[x, y] = piece
            state.gameState[oldX, oldY] = "  "
            state.sith[sithIndex] = (piece, x, y)
        elif state.gameState[x, y][0] == "J":
            # if the sith is moving to a spot with a jedi
            if (state.gameState[x, y], x, y) in state.jedi:
                jediIndex = state.jedi.index((state.gameState[x, y], x, y))
                state.gameState[x, y] = "S" + str(len(state.sith))
                state.sith.append(("S" + str(len(state.sith)), x, y))
                del state.jedi[jediIndex]
        elif state.gameState[x, y][0] == "R":
            # if the sith is moving to a spot with a rebel
            rebelIndex = state.rebels.index((state.gameState[x, y], x, y))
            sithIndex = state.sith.index((piece, oldX, oldY))
            state.gameState[x, y] = piece
            state.gameState[oldX, oldY] = "  "
            state.sith[sithIndex] = (piece, x, y)
            del state.rebels[rebelIndex]
        return state

    def updateRebels(self, state, action):
        """ Return the state that results from the application of the
            given action in the given state.
            :param state: a legal game state
            :param action: a legal action in the game state
            :return: a new game state
        """
        who, piece, x, y, oldX, oldY = action
        if state.gameState[x, y] == "  ":
            if x == 0:
                # if a rebel is moving to an empty spot in the top row,  to convert it to a jedi
                rebelIndex = state.rebels.index((piece, oldX, oldY))
                state.gameState[x, y] = "J" + str(len(state.jedi))
                state.jedi.append(("J" + str(len(state.jedi)), x, y))
                state.gameState[oldX, oldY] = "  "
                del state.rebels[rebelIndex]
            else:
                # else the spot is not in the top row and move normally
                rebelIndex = state.rebels.index((piece, oldX, oldY))
                state.gameState[x, y] = piece
                state.rebels[rebelIndex] = (piece, x, y)
                state.gameState[oldX, oldY] = "  "
        elif state.gameState[x, y][0] == "S":
            if x == 0:
                # if the spot is in the top row, and a sith is there, remove the sith and upgrade rebel to jedi
                rebelIndex = state.rebels.index((piece, oldX, oldY))
                sithIndex = state.sith.index((state.gameState[x, y], x, y))
                state.gameState[x, y] = "J" + str(len(state.jedi))
                state.jedi.append(("J" + str(len(state.jedi)), x, y))
                state.gameState[oldX, oldY] = "  "
                del state.rebels[rebelIndex]
                del state.sith[sithIndex]
            else:
                # else remove the sith
                rebelIndex = state.rebels.index((piece, oldX, oldY))
                sithIndex = state.sith.index((state.gameState[x, y], x, y))
                del state.sith[sithIndex]
                state.gameState[x, y] = piece
                state.gameState[oldX, oldY] = "  "
                state.rebels[rebelIndex] = (piece, x, y)
        return state

    def utility(self, state):
        """ Calculate the utility of the given state.
            :param state: a legal game state
            :return: utility of the terminal state
        """
        # Make sure Utility and Eval use the same values to determine winners
        if state.cachedWin and state.cachedWinner:
            return 61  # Rebel forces
        elif state.cachedWin and not state.cachedWinner:
            return -61  # Sith Forces
        else:
            return 0  # Everyone succ

    def cutoff_test(self, state, depth):
        """
            Check if the search should be cut-off early.
            In a more interesting game, you might look at the state
            and allow a deeper search in important branches, and a shallower
            search in boring branches.

            :param state: a game state
            :param depth: the depth of the state,
                          in terms of levels below the start of search.
            :return: True if search should be cut off here.
        """
        # print(self.depthLimit > 0 and depth > self.depthLimit)
        return self.depthLimit > 0 and depth > self.depthLimit

    def eval(self, state):
        """
            When a depth limit is applied, we need to evaluate the
            given state to estimate who might win.
            state: a legal game state
            :return: a numeric value in the range of the utility function
        """
        # eval is described in A4Q4.txt
        weights = {"S": 10, "J": 8, "R": 1}
        turnBonus = 0
        rebelCount = len(state.rebels)
        sithCount = len(state.sith)
        jediCount = len(state.jedi)
        if state.maxsTurn:
            turnBonus = 10
        else:
            turnBonus = -10
        return turnBonus + (rebelCount * weights["R"]) + (jediCount * weights["J"]) - (sithCount * weights["S"])

    def congratulate(self, state):
        """ Called at the end of a game, display some appropriate 
            sentiments to the console. Could be used to display 
            game statistics as well.
            :param state: a legal game state
        """
        winstring = 'Congratulations, {} wins (utility: {})'
        if state.cachedWin and state.cachedWinner:
            print(winstring.format("Rebel forces", self.utility(state)))
            return "Rebels"
        elif state.cachedWin and not state.cachedWinner:
            print(winstring.format("Sith", self.utility(state)))
            return "Sith"
        else:
            print('No winner')

    def transposition_string(self, state):
        """ Returns a unique string for the given state.  For use in 
            any Game Tree Search that employs a transposition table.
            :param state: a legal game state
            :return: a unique string representing the state
        """
        return state.string

    def _cache_winner(self, who, x, y, state):
        """ Look at the board and check if the new move was a winner.
            If we look right after a move, we can reduce the effort
            needed to check.  We only have to look at the triplets
            passing through the move!
            :param: who
            :param: where
            :param state: a legal game state
            :return:
        """
        # where is a tuple (row, col)
        recent_r, recent_c = x, y

        # because we know who just moved, we only have to
        # check for wins for that player
        if who:
            token = "Rebels"
        else:
            token = "Sith"

        if len(state.jedi) + len(state.rebels) == 0:
            won = True
        elif len(state.sith) == 0:
            won = True
        else:
            won = False

        if won:
            state.cachedWin = True
            state.cachedWinner = who

        return  # not really needed, but indicates the end of the method

# eof
