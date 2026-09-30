Ultimate (or 9x9) Tic Tac Toe
=============================

What is this thing?  See
`http://mathwithbaddrawings.com/2013/06/16/ultimate-tic-tac-toe/` for details.


Requirements
------------

* Python 3.10+; PyPy; PyPy3


Getting Started
---------------

To set up your local environment you should create a virtualenv and
install everything into it. ::

    $ mkvirtualenv tictactoe

Pip install this repo, either from a local copy, ::

    $ pip install -e ultimate_tictactoe

or from github, ::

    $ pip install git+https://github.com/jbradberry/ultimate_tictactoe#egg=ut3

and then install the requirements ::

    $ pip install -r requirements_server.txt
    $ pip install -r requirements_player.txt

To run the server with Ultimate Tic Tac Toe ::

    $ board-serve t3

Optionally, the server ip address and port number can be added ::

    $ board-serve t3 0.0.0.0
    $ board-serve t3 0.0.0.0 8000

To connect a client as a human player ::

    $ board-play t3 human
    $ board-play t3 human 192.168.1.1 8000   # with ip addr and port

To connect a client using one of the compatible `Monte Carlo Tree
Search AI <https://github.com/jbradberry/mcts>`_ players ::

    $ board-play t3 jrb.mcts.uct    # number of wins metric
    $ board-play t3 jrb.mcts.uctv   # point value of the board metric
