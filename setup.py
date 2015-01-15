from distutils.core import setup

setup(
    name='UltimateTicTacToe',
    version='0.1dev',
    author='Jeff Bradberry',
    author_email='jeff.bradberry@gmail.com',
    packages=['t3'],
    entry_points={
        'jrb_board.games': 't3 = t3.board:Board',
        'jrb_board.players': 't3.jrb_mcts = t3.mcts:MonteCarlo',
    },
    license='LICENSE',
    description="An implementation of Ultimate Tic Tac Toe.",
)
