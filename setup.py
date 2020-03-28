from __future__ import absolute_import
from distutils.core import setup

setup(
    name='UltimateTicTacToe',
    version='0.8.0-dev',
    author='Jeff Bradberry',
    author_email='jeff.bradberry@gmail.com',
    packages=['t3'],
    entry_points={
        'jrb_board.games': 't3 = t3.board:Board',
    },
    install_requires=['six'],
    license='LICENSE',
    description="An implementation of Ultimate Tic Tac Toe.",
)
