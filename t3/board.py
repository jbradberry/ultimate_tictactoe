

class Board(object):
    num_players = 2

    wins = (
        0b000000111, 0b000111000, 0b111000000,
        0b100100100, 0b010010010, 0b001001001,
        0b100010001, 0b001010100
    )

    def starting_state(self):
        # Each of the 9 pairs of player 1 and player 2 board bitmasks
        # plus the win/tie state of the big board for p1 and p2 plus
        # the row and column of the required board for the next action
        # and finally the player number to move.
        return (0, 0) * 10 + (None, None, 1)

    def display(self, state, action, _unicode=True):
        actions = {
            (R, C, r, c): p
            for R in xrange(3)
            for C in xrange(3)
            for r in xrange(3)
            for c in xrange(3)
            for i, p in enumerate('XO')
            if state[2*(3*R + C) + i] & 1 << (3 * r + c)
        }

        player = state[-1]

        sub = u"\u2564".join(u"\u2550" for x in xrange(3))
        top = u"\u2554" + u"\u2566".join(sub for x in xrange(3)) + u"\u2557\n"

        sub = u"\u256a".join(u"\u2550" for x in xrange(3))
        div = u"\u2560" + u"\u256c".join(sub for x in xrange(3)) + u"\u2563\n"

        sub = u"\u253c".join(u"\u2500" for x in xrange(3))
        sep = u"\u255f" + u"\u256b".join(sub for x in xrange(3)) + u"\u2562\n"

        sub = u"\u2567".join(u"\u2550" for x in xrange(3))
        bot = u"\u255a" + u"\u2569".join(sub for x in xrange(3)) + u"\u255d\n"
        if action:
            bot += u"Last played: {0}\n".format(self.unpack_action(action))
        bot += u"Player: {0}\n".format(player)

        return (
            top +
            div.join(
                sep.join(
                    u"\u2551" +
                    u"\u2551".join(
                        u"\u2502".join(
                            actions.get((R, C, r, c), " ") for c in xrange(3)
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

    def pack_state(self, data):
        state = [0] * 20
        state.extend([data['constraint']['outer-row'],
                      data['constraint']['outer-column'],
                      data['player']])

        for item in data['pieces']:
            R, C, player = item['outer-row'], item['outer-column'], item['player']
            r, c = item['inner-row'], item['inner-column']
            state[2*(3*R + C) + player - 1] += 1 << (3 * r + c)

        for item in data['boards']:
            players = (1, 2)
            if item['player'] is not None:
                players = (item['player'],)

            for player in players:
                state[17 + player] += 1 << (3 * item['outer-row'] + item['outer-column'])

        return tuple(state)

    def unpack_state(self, state):
        player = state[-1]
        p1_boards, p2_boards = state[18], state[19]

        pieces, boards = [], []
        for R in xrange(3):
            for C in xrange(3):
                for r in xrange(3):
                    for c in xrange(3):
                        index = 1 << (3 * r + c)

                        if index & state[2*(3*R + C)]:
                            pieces.append({
                                'player': 1, 'type': 'X',
                                'outer-row': R, 'outer-column': C,
                                'inner-row': r, 'inner-column': c,
                            })
                        if index & state[2*(3*R + C) + 1]:
                            pieces.append({
                                'player': 2, 'type': 'O',
                                'outer-row': R, 'outer-column': C,
                                'inner-row': r, 'inner-column': c,
                            })

                board_index = 1 << (3 * R + C)
                if board_index & p1_boards & p2_boards:
                    boards.append({
                        'player': None, 'type': 'full',
                        'outer-row': R, 'outer-column': C,
                    })
                elif board_index & p1_boards:
                    boards.append({
                        'player': 1, 'type': 'X',
                        'outer-row': R, 'outer-column': C,
                    })
                elif board_index & p2_boards:
                    boards.append({
                        'player': 2, 'type': 'O',
                        'outer-row': R, 'outer-column': C,
                    })

        return {
            'pieces': pieces,
            'boards': boards,
            'constraint': {'outer-row': state[20], 'outer-column': state[21]},
            'player': player,
            'previous_player': 3 - player,
        }

    def pack_action(self, notation):
        try:
            R, C, r, c = map(int, notation.split())
        except Exception:
            return
        return R, C, r, c

    def unpack_action(self, action):
        try:
            return '{0} {1} {2} {3}'.format(*action)
        except Exception:
            return ''

    def next_state(self, state, action):
        R, C, r, c = action
        player = state[-1]
        board_index = 6 * R + 2 * C  # 2*(3*R + C)
        player_index = player - 1

        small_position = 1 << (3 * r + c)
        large_position = 1 << (3 * R + C)

        state = list(state)
        state[-1] = 3 - player
        state[board_index + player_index] |= small_position
        updated_board = state[board_index + player_index]

        full = (state[board_index] | state[board_index+1] == 0x1ff)
        if any(updated_board & w == w for w in self.wins):
            state[18 + player_index] |= large_position
        elif full:
            state[18] |= large_position
            state[19] |= large_position

        if (state[18] | state[19]) & small_position:
            state[20], state[21] = None, None
        else:
            state[20], state[21] = r, c

        return tuple(state)

    def is_legal(self, history, action):
        state = history[-1]
        R, C, r, c = action

        # Is action out of bounds?
        if not (0 <= R < 3):
            return False
        if not (0 <= C < 3):
            return False
        if not (0 <= r < 3):
            return False
        if not (0 <= c < 3):
            return False

        player = state[-1]
        board_index = 2*(3*R + C)
        player_index = player - 1

        # Is the square within the sub-board already taken?
        occupied = state[board_index] | state[board_index+1]
        if occupied & 1 << (3 * r + c):
            return False

        # Is our action unconstrained by the previous action?
        if state[20] is None:
            return True

        # Otherwise, we must play in the proper sub-board.
        return (R, C) == (state[20], state[21])

    def legal_actions(self, history):
        state = history[-1]
        R, C = state[20], state[21]
        Rset, Cset = (R,), (C,)
        if R is None:
            Rset, Cset = range(3), range(3)

        occupied = [
            state[2*x] | state[2*x+1] for x in xrange(9)
        ]
        finished = state[18] | state[19]

        return [
            (R, C, r, c)
            for R in Rset
            for C in Cset
            for r in xrange(3)
            for c in xrange(3)
            if not occupied[3*R+C] & 1 << (3 * r + c)
            and not finished & 1 << (3 * R + C)
        ]

    def previous_player(self, state):
        return 3 - state[-1]

    def current_player(self, state):
        return state[-1]

    def is_ended(self, history):
        state = history[-1]
        p1 = state[18] & ~state[19]
        p2 = state[19] & ~state[18]

        if any(w & p1 == w for w in self.wins):
            return True
        if any(w & p2 == w for w in self.wins):
            return True
        if state[18] | state[19] == 0x1ff:
            return True

        return False

    def win_values(self, history):
        if not self.is_ended(history):
            return

        state = history[-1]
        p1 = state[18] & ~state[19]
        p2 = state[19] & ~state[18]

        if any(w & p1 == w for w in self.wins):
            return {1: 1, 2: 0}
        if any(w & p2 == w for w in self.wins):
            return {1: 0, 2: 1}
        if state[18] | state[19] == 0x1ff:
            return {1: 0.5, 2: 0.5}

    def points_values(self, history):
        if not self.is_ended(history):
            return

        state = history[-1]
        p1 = state[18] & ~state[19]
        p2 = state[19] & ~state[18]

        if any(w & p1 == w for w in self.wins):
            return {1: 1, 2: -1}
        if any(w & p2 == w for w in self.wins):
            return {1: -1, 2: 1}
        if state[18] | state[19] == 0x1ff:
            return {1: 0, 2: 0}

    def winner_message(self, winners):
        winners = sorted((v, k) for k, v in winners.iteritems())
        value, winner = winners[-1]
        if value == 0.5:
            return "Draw."
        return "Winner: Player {0}.".format(winner)
