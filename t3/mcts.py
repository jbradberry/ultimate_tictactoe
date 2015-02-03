from __future__ import division

from random import random, choice
from math import log, sqrt
import datetime


class BasePlayer(object):
    def __init__(self, board, *args, **kwargs):
        self.board = board
        self.player = None
        self.states = []

    def update(self, state):
        self.states.append(state)

    def display(self, state, play):
        return self.board.display(state, play)

    def winner_message(self, msg):
        return self.board.winner_message(msg)


class MonteCarlo(BasePlayer):
    def __init__(self, board, **kwargs):
        super(MonteCarlo, self).__init__(board, **kwargs)
        self.max_moves = 9 * 9
        self.max_time = datetime.timedelta(seconds=5)
        self.C = kwargs.get('C', 1.4)
        self.wins = {1: {}, 2: {}}
        self.plays = {1: {}, 2: {}}

    def get_play(self):
        state = self.states[-1]
        player = state[-1]
        legal = self.board.legal_plays(state)

        if not legal:
            return
        if len(legal) == 1:
            return legal[0]

        states = [(p, self.board.play(state, p)) for p in legal]

        begin, games = datetime.datetime.utcnow(), 0
        while datetime.datetime.utcnow() - begin < self.max_time:
            self.random_game()
            games += 1

        print games, datetime.datetime.utcnow() - begin
        move = max(
            (self.wins[player].get(S,0) / self.plays[player].get(S,1), p)
            for p, S in states
        )[1]

        for x in sorted(((100 * self.wins[player].get(S,0)
                          / self.plays[player].get(S,1),
                          self.wins[player].get(S,0),
                          self.plays[player].get(S,0), p)
                         for p, S in states), reverse=True):
            print "{3}: {0:.2f}% ({1} / {2})".format(*x)

        return move

    def random_game(self):
        game_moves = {1: set(), 2: set()}
        new_states = self.states[:]

        expand = True
        for t in xrange(self.max_moves):
            state = new_states[-1]
            player = state[-1]
            legal = self.board.legal_plays(state)
            states = [(p, self.board.play(state, p)) for p in legal]

            plays, wins = self.plays[player], self.wins[player]
            if all(plays.get(S) for p, S in states):
                log_total = log(sum(plays[S] for p, S in states))
                move, state = max(((wins[S] / plays[S]) +
                                   self.C * sqrt(log_total / plays[S]), p, S)
                                  for p, S in states)[1:]
            else:
                move, state = choice(states)

            new_states.append(state)

            if expand and state not in plays:
                expand = False
                plays[state] = 0
                wins[state] = 0

            game_moves[player].add(state)

            winner = self.board.winner(new_states)
            if winner:
                break

        for player, M in game_moves.iteritems():
            for S in M:
                if S in self.plays[player]:
                    self.plays[player][S] += 1
        if winner in (1, 2):
            for S in game_moves[winner]:
                if S in self.plays[winner]:
                    self.wins[winner][S] += 1
