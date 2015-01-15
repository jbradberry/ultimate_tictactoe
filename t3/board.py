

class Board(object):
    num_players = 2

    positions = dict(
        ((R, C, r, c), 1<<(27*R + 9*r + 3*C + c))
        for R in xrange(3)
        for C in xrange(3)
        for r in xrange(3)
        for c in xrange(3)
    )

    inv_positions = dict(
        (v, P) for P, v in positions.iteritems()
    )

    wins = [
        frozenset((0, C) for C in xrange(3)),
        frozenset((1, C) for C in xrange(3)),
        frozenset((2, C) for C in xrange(3)),
        frozenset((R, 0) for R in xrange(3)),
        frozenset((R, 1) for R in xrange(3)),
        frozenset((R, 2) for R in xrange(3)),
        frozenset((R, R) for R in xrange(3)),
        frozenset((R, 2-R) for R in xrange(3)),
    ]

    def start(self):
        return (0, 0, (), 1)

    def display(self, state, play, _unicode=True):
        p1, p2, lastplay, player = state
        plays = {}
        for (R, C, r, c), val in self.positions.iteritems():
            piece = u" "
            if val & p1:
                piece = u'X'
            elif val & p2:
                piece = u'O'
            plays[(R, C, r, c)] = piece

        sub = u"\u2564".join(u"\u2550" for x in xrange(3))
        top = u"\u2554" + u"\u2566".join(sub for x in xrange(3)) + u"\u2557\n"

        sub = u"\u256a".join(u"\u2550" for x in xrange(3))
        div = u"\u2560" + u"\u256c".join(sub for x in xrange(3)) + u"\u2563\n"

        sub = u"\u253c".join(u"\u2500" for x in xrange(3))
        sep = u"\u255f" + u"\u256b".join(sub for x in xrange(3)) + u"\u2562\n"

        sub = u"\u2567".join(u"\u2550" for x in xrange(3))
        bot = u"\u255a" + u"\u2569".join(sub for x in xrange(3)) + u"\u255d\n"
        if play:
            bot += u"Last played: {0}\n".format(self.pack(play))
        bot += u"Player: {0}\n".format(player)

        return (
            top +
            div.join(
                sep.join(
                    u"\u2551" +
                    u"\u2551".join(
                        u"\u2502".join(
                            plays[(R, C, r, c)] for c in xrange(3)
                        )
                        for C in xrange(3)
                    ) +
                    u"\u2551\n"
                    for r in xrange(3)
                )
                for R in xrange(3)
            ) +
            bot
        )

    def parse(self, play):
        try:
            R, C, r, c = map(int, play.split())
        except Exception:
            return
        return R, C, r, c

    def pack(self, play):
        try:
            return '{0} {1} {2} {3}'.format(*play)
        except Exception:
            return ''

    def play(self, state, play):
        p1, p2, lastplay, player = state
        positions = {1: p1, 2: p2}
        positions[player] |= self.positions[play]
        return positions[1], positions[2], play[2:], 3 - player

    def is_legal(self, state, play):
        # Is play out of bounds?
        if play not in self.positions:
            return False

        # Is this the first play?
        p1state, p2state, lastplay, player = state
        if not lastplay:
            return True

        # Is the square already taken?
        occupied = p1state | p2state
        if self.positions[play] & occupied:
            return False

        # Is the corresponding sub-board already won?
        finished = self.finished_boards(state)
        if lastplay in finished:
            return play[:2] not in finished

        # Otherwise, we must play in the proper sub-board.
        return play[:2] == lastplay

    def finished_boards(self, state):
        finished, positions = {}, {}
        p1, p2, lastplay, player = state
        for (R, C, r, c), val in self.positions.iteritems():
            subboard = positions.setdefault((R, C), {1: set(), 2: set()})
            if val & p1:
                subboard[1].add((r, c))
            elif val & p2:
                subboard[2].add((r, c))

        for (R, C), subboard in positions.iteritems():
            for player in subboard:
                if any(winset <= subboard[player] for winset in self.wins):
                    finished[(R, C)] = player
                    break
            if len(subboard[1]) + len(subboard[2]) == 9:
                finished.setdefault((R, C), 3)

        return finished

    def legal_plays(self, state):
        p1, p2, lastplay, player = state
        occupied = p1 | p2

        if not lastplay:
            return self.positions.keys()

        finished = self.finished_boards(state)

        plays = [
            (R, C, r, c) for (R, C, r, c), val in self.positions.iteritems()
            if not val & occupied
            and (R, C) not in finished
            and (lastplay == (R, C) or lastplay in finished)
        ]

        return plays

    def next_player(self, state):
        return state[-1]

    def winner(self, state_lst):
        state = state_lst[-1]
        finished = self.finished_boards(state)

        for player in (1, 2):
            boards_won = set(
                board for board, p in finished.iteritems()
                if p == player
            )

            if any(winset <= boards_won for winset in self.wins):
                return player

        if len(finished) == 9:
            return 3
        return 0

    def winner_message(self, winner):
        if winner == 3:
            return "Draw."
        return "Winner: Player {0}.".format(winner)
