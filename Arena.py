import numpy as np
from pytorch_classification.utils import Bar, AverageMeter
import time


class Arena():
    """
    An Arena class where any 2 agents can be pit against each other.
    """

    def __init__(self, player1, player2, game, mcts1=None,mcts2=None,evaluate=False,display=None,name=None):
        """
        Input:
            player 1,2: two functions that takes board as input, return action
            game: Game object
            display: a function that takes board as input and prints it (e.g.
                     display in othello/OthelloGame). Is necessary for verbose
                     mode.
            mcts1/mcts2: represernts the MonteCarloTrees used by the two networks(in case when we pit one against the other)
                    or used by a single network when pit against an  agent(greedy, minmax,random)
            evaluate: used only in pitting the network against itself and minimax because i want some randomness in the
                    first move in order to evaluate the network better
        see othello/OthelloPlayers.py for an example. See pit.py for pitting
        human players/other baselines with each other.
        """
        self.player1 = player1
        self.player2 = player2
        self.game = game
        self.display = display
        self.mcts1=mcts1
        self.mcts2=mcts2
        self.evaluate=evaluate
        self.name=name

    def clearMCTS(self):
        if self.mcts1:
            self.mcts1.clear()
        if self.mcts2:
            self.mcts2.clear()

    def clearArena(self):
        self.player1 = None
        self.player2 = None
        self.game = None
        self.display = None
        self.mcts1 = None
        self.mcts2 = None
        self.evaluate = None

    def playGame(self, verbose=False):
        """
        Executes one episode of a game.
        verbose: used to display the game in the console, otetwhise it will not draw it
        Returns:
            either
                winner: player who won the game (1 if player1, -1 if player2)
            or
                draw result returned from the game that is neither 1, -1, nor 0.
        """
        players = [self.player2, None, self.player1]
        curPlayer = 1
        board = self.game.getInitBoard()

        if verbose:
            self.display(board)
        self.clearMCTS()
        it = 0
        while self.game.getGameEnded(board, curPlayer) == 0:
            it += 1

            action = players[curPlayer + 1](self.game.getCanonicalForm(board, curPlayer))

            valids = self.game.getValidMoves(self.game.getCanonicalForm(board, curPlayer), 1)

            if verbose:
                assert (self.display)
                print("Turn ", str(it), "Player ", str(curPlayer))

            if it<=1 and self.evaluate==True and self.name!="gobang":
                print("intru in asta")
                while True:
                    random_action = np.random.randint(0, self.game.getActionSize() - 1)
                    if valids[random_action]==1:
                        action=random_action
                        break
            elif it==2 and self.evaluate==True and self.name=="gobang":
                print("intru in asta")
                while True:
                    random_action = np.random.randint(0, self.game.getActionSize() - 1)
                    if valids[random_action]==1:
                        action=random_action
                        break

            elif valids[action] == 0:
                print(action)
                assert valids[action] > 0

            board, curPlayer = self.game.getNextState(board, curPlayer, action)

            if verbose:
                assert (self.display)
                self.display(board)

        if verbose:
            assert (self.display)
            print("Game over: Turn ", str(it), "Result ", str(self.game.getGameEnded(board, 1)))
            self.display(board)
        return self.game.getGameEnded(board, 1)

    def playGames(self, num, verbose=False):
        """
        Plays num games in which player1 starts num/2 games and player2 starts
        verbose: used to display the game in the console, otetwhise it will not draw it
        num/2 games.
        Returns:
            oneWon: games won by player1
            twoWon: games won by player2
            draws:  games won by nobody
        """
        eps_time = AverageMeter()
        bar = Bar('Arena.playGames', max=num)
        end = time.time()
        eps = 0
        maxeps = int(num)

        num = int(num / 2)
        oneWon = 0
        twoWon = 0
        draws = 0
        for _ in range(num):
            gameResult = self.playGame(verbose=verbose)
            if gameResult == 1:
                oneWon += 1
            elif gameResult == -1:
                twoWon += 1
            else:
                draws += 1
            # bookkeeping + plot progress
            eps += 1
            eps_time.update(time.time() - end)
            end = time.time()
            bar.suffix = '({eps}/{maxeps}) Eps Time: {et:.3f}s | Total: {total:} | ETA: {eta:}'.format(eps=eps + 1,
                                                                                                       maxeps=maxeps,
                                                                                                       et=eps_time.avg,
                                                                                                       total=bar.elapsed_td,
                                                                                                       eta=bar.eta_td)
            bar.next()

        self.player1, self.player2 = self.player2, self.player1

        for _ in range(num):
            gameResult = self.playGame(verbose=verbose)
            if gameResult == -1:
                oneWon += 1
            elif gameResult == 1:
                twoWon += 1
            else:
                draws += 1
            # bookkeeping + plot progress
            eps += 1
            eps_time.update(time.time() - end)
            end = time.time()
            bar.suffix = '({eps}/{maxeps}) Eps Time: {et:.3f}s | Total: {total:} | ETA: {eta:}'.format(eps=eps + 1,
                                                                                                       maxeps=num,
                                                                                                       et=eps_time.avg,
                                                                                                       total=bar.elapsed_td,
                                                                                                       eta=bar.eta_td)
            bar.next()

        bar.finish()
        self.clearArena()
        return oneWon, twoWon, draws
