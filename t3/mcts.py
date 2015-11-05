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
        self.max_depth = 0
        self.stats = None

    def get_play(self):
        self.max_depth = 0
        self.stats = {}

        state = self.states[-1]
        player = state[-1]
        legal = self.board.legal_plays([state])

        if not legal:
            return
        if len(legal) == 1:
            return legal[0]

        states = [(p, self.board.next_state(state, p)) for p in legal]

        begin, games = datetime.datetime.utcnow(), 0
        while datetime.datetime.utcnow() - begin < self.max_time:
            self.random_game()
            games += 1

        self.stats.update(games=games, max_depth=self.max_depth,
                          time=str(datetime.datetime.utcnow() - begin))
        print self.stats['games'], self.stats['time']
        print "Maximum depth searched:", self.max_depth

        self.stats['moves'] = sorted(
            ({'move': p,
              'percent': 100 * self.wins[player].get(S,0) / self.plays[player].get(S,1),
              'wins': self.wins[player].get(S,0),
              'plays': self.plays[player].get(S,0)}
             for p, S in states),
            key=lambda x: (x['percent'], x['plays']),
            reverse=True,
        )
        for m in self.stats['moves']:
            print "{move}: {percent:.2f}% ({wins} / {plays})".format(**m)

        move = max(
            (self.wins[player].get(S,0) / self.plays[player].get(S,1), p)
            for p, S in states
        )[1]

        return move

    def random_game(self):
        game_moves = {1: set(), 2: set()}
        new_states = self.states[:]

        expand = True
        for t in xrange(1, self.max_moves + 1):
            state = new_states[-1]
            player = state[-1]
            legal = self.board.legal_plays([state])
            states = [(p, self.board.next_state(state, p)) for p in legal]

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
                if t > self.max_depth:
                    self.max_depth = t

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
