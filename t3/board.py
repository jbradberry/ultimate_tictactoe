import six
from six.moves import map
from six.moves import range


class Board(object):
    num_players = 2

    def starting_state(self):
        # Each of the 9 pairs of player 1 and player 2 board bitmasks
        # plus the win/tie state of the big board for p1 and p2 plus
        # the row and column of the required board for the next action
        # and finally the player number to move.
        return (0, 0) * 10 + (None, None, 1)

    def display(self, state, action, _unicode=True):
        pieces = {
            (slot['outer-row'], slot['outer-column'],
             slot['inner-row'], slot['inner-column']): slot['type']
            for slot in state['pieces']
        }

        sub = u"\u2564".join(u"\u2550" for x in range(3))
        top = u"\u2554" + u"\u2566".join(sub for x in range(3)) + u"\u2557\n"

        sub = u"\u256a".join(u"\u2550" for x in range(3))
        div = u"\u2560" + u"\u256c".join(sub for x in range(3)) + u"\u2563\n"

        sub = u"\u253c".join(u"\u2500" for x in range(3))
        sep = u"\u255f" + u"\u256b".join(sub for x in range(3)) + u"\u2562\n"

        sub = u"\u2567".join(u"\u2550" for x in range(3))
        bot = u"\u255a" + u"\u2569".join(sub for x in range(3)) + u"\u255d\n"
        if action:
            bot += u"Last played: {0}\n".format(
                self.to_notation(self.to_compact_action(action)))
        bot += u"Player: {0}\n".format(state['player'])

        constraint = (state['constraint']['outer-row'], state['constraint']['outer-column'])

        return (
            top +
            div.join(
                sep.join(
                    u"\u2551" +
                    u"\u2551".join(
                        u"\u2502".join(
                            pieces.get((R, C, r, c), u"\u2592" if constraint in ((R, C), (None, None)) else " ")
                            for c in range(3)
                        )
                        for C in range(3)
                    ) +
                    u"\u2551\n"
                    for r in range(3)
                )
                for R in range(3)
            ) +
            bot
        )

    def to_compact_state(self, data):
        state = [0] * 20
        state.extend([
            data['constraint']['outer-row'],
            data['constraint']['outer-column'],
            data['player']
        ])

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

    def to_json_state(self, state):
        player = state[-1]
        p1_boards, p2_boards = state[18], state[19]

        pieces, boards = [], []
        for R in range(3):
            for C in range(3):
                for r in range(3):
                    for c in range(3):
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

    def to_compact_action(self, action):
        return (
            action['outer-row'], action['outer-column'],
            action['inner-row'], action['inner-column']
        )

    def to_json_action(self, action):
        try:
            R, C, r, c = action
            return {
                'outer-row': R, 'outer-column': C,
                'inner-row': r, 'inner-column': c,
            }
        except Exception:
            return {}

    def from_notation(self, notation):
        try:
            R, C, r, c = list(map(int, notation.split()))
        except Exception:
            return
        return R, C, r, c

    def to_notation(self, action):
        return ' '.join(map(str, action))

    def next_state(self, history, action):
        state = history[-1]
        R, C, r, c = action
        player = state[-1]
        board_index = 2 * (3 * R + C)
        player_index = player - 1

        state = list(state)
        state[-1] = 3 - player
        state[board_index + player_index] |= 1 << (3 * r + c)
        updated_board = state[board_index + player_index]

        wins = (0o7, 0o70, 0o700, 0o111, 0o222, 0o444, 0o421, 0o124)

        full = (state[board_index] | state[board_index+1] == 0o777)
        if any(updated_board & w == w for w in wins):
            state[18 + player_index] |= 1 << (3 * R + C)
        elif full:
            state[18] |= 1 << (3 * R + C)
            state[19] |= 1 << (3 * R + C)

        if (state[18] | state[19]) & 1 << (3 * r + c):
            state[20], state[21] = None, None
        else:
            state[20], state[21] = r, c

        return tuple(state)

    def is_legal(self, state, action):
        R, C, r, c = action

        # Is action out of bounds?
        if not (0 <= R <= 2):
            return False
        if not (0 <= C <= 2):
            return False
        if not (0 <= r <= 2):
            return False
        if not (0 <= c <= 2):
            return False

        player = state[-1]
        board_index = 2 * (3 * R + C)
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

    def legal_actions(self, state):
        R, C = state[20], state[21]
        Rset, Cset = (R,), (C,)
        if R is None:
            Rset = Cset = (0, 1, 2)

        occupied = [
            state[2 * x] | state[2 * x + 1] for x in range(9)
        ]
        finished = state[18] | state[19]

        actions = [
            (R, C, r, c)
            for R in Rset
            for C in Cset
            for r in range(3)
            for c in range(3)
            if not occupied[3 * R + C] & 1 << (3 * r + c)
            and not finished & 1 << (3 * R + C)
        ]

        return actions

    def previous_player(self, state):
        return 3 - state[-1]

    def current_player(self, state):
        return state[-1]

    def is_ended(self, state):
        p1 = state[18] & ~state[19]
        p2 = state[19] & ~state[18]

        wins = (0o7, 0o70, 0o700, 0o111, 0o222, 0o444, 0o421, 0o124)

        if any(w & p1 == w for w in wins):
            return True
        if any(w & p2 == w for w in wins):
            return True
        if state[18] | state[19] == 0o777:
            return True

        return False

    def win_values(self, state):
        if not self.is_ended(state):
            return

        p1 = state[18] & ~state[19]
        p2 = state[19] & ~state[18]

        wins = (0o7, 0o70, 0o700, 0o111, 0o222, 0o444, 0o421, 0o124)

        if any(w & p1 == w for w in wins):
            return {1: 1, 2: 0}
        if any(w & p2 == w for w in wins):
            return {1: 0, 2: 1}
        if state[18] | state[19] == 0o777:
            return {1: 0.5, 2: 0.5}

    def points_values(self, state):
        if not self.is_ended(state):
            return

        p1 = state[18] & ~state[19]
        p2 = state[19] & ~state[18]

        wins = (0o7, 0o70, 0o700, 0o111, 0o222, 0o444, 0o421, 0o124)

        if any(w & p1 == w for w in wins):
            return {1: 1, 2: -1}
        if any(w & p2 == w for w in wins):
            return {1: -1, 2: 1}
        if state[18] | state[19] == 0o777:
            return {1: 0, 2: 0}

    def winner_message(self, winners):
        winners = sorted((v, k) for k, v in six.iteritems(winners))
        value, winner = winners[-1]
        if value == 0.5:
            return "Draw."
        return "Winner: Player {0}.".format(winner)
