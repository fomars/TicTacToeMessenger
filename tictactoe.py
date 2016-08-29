# coding=utf-8
# Tic Tac Toe
import os
import random

import requests
from flask import current_app as app

player_sessions = {}
message_strings = None


def drawBoard(board, player_id, send_message):
    # This function prints out the board that it was passed.

    # "board" is a list of 10 strings representing the board (ignore index 0)
    index = 1
    message = ''
    while index < 10:
        message += ' '.join(board[index:index + 3])
        message += '\n'
        index += 3

    send_message(player_id, message)


def makeMove(board, letter, move):
    board[move] = letter


def isWinner(bo, le):
    # Given a board and a player's letter, this function returns True if that player has won.
    # We use bo instead of board and le instead of letter so we don't have to type as much.
    return ((bo[7] == le and bo[8] == le and bo[9] == le) or  # across the top
            (bo[4] == le and bo[5] == le and bo[6] == le) or  # across the middle
            (bo[1] == le and bo[2] == le and bo[3] == le) or  # across the bottom
            (bo[7] == le and bo[4] == le and bo[1] == le) or  # down the left side
            (bo[8] == le and bo[5] == le and bo[2] == le) or  # down the middle
            (bo[9] == le and bo[6] == le and bo[3] == le) or  # down the right side
            (bo[7] == le and bo[5] == le and bo[3] == le) or  # diagonal
            (bo[9] == le and bo[5] == le and bo[1] == le))  # diagonal


def getBoardCopy(board):
    # Make a duplicate of the board list and return it the duplicate.
    dupeBoard = []

    for i in board:
        dupeBoard.append(i)

    return dupeBoard


def isSpaceFree(board, move):
    # Return true if the passed move is free on the passed board.
    return board[move] == '_'


def chooseRandomMoveFromList(board, movesList):
    # Returns a valid move from the passed list on the passed board.
    # Returns None if there is no valid move.
    possibleMoves = []
    for i in movesList:
        if isSpaceFree(board, i):
            possibleMoves.append(i)

    if len(possibleMoves) != 0:
        return random.choice(possibleMoves)
    else:
        return None


def getComputerMove(board, computerLetter):
    # Given a board and the computer's letter, determine where to move and return that move.
    if computerLetter == 'X':
        playerLetter = 'O'
    else:
        playerLetter = 'X'

    # Here is our algorithm for our Tic Tac Toe AI:
    # First, check if we can win in the next move
    for i in range(1, 10):
        copy = getBoardCopy(board)
        if isSpaceFree(copy, i):
            makeMove(copy, computerLetter, i)
            if isWinner(copy, computerLetter):
                return i

    # Check if the player could win on his next move, and block them.
    for i in range(1, 10):
        copy = getBoardCopy(board)
        if isSpaceFree(copy, i):
            makeMove(copy, playerLetter, i)
            if isWinner(copy, playerLetter):
                return i

    # Try to take one of the corners, if they are free.
    move = chooseRandomMoveFromList(board, [1, 3, 7, 9])
    if move != None:
        return move

    # Try to take the center, if it is free.
    if isSpaceFree(board, 5):
        return 5

    # Move on one of the sides.
    return chooseRandomMoveFromList(board, [2, 4, 6, 8])


def isBoardFull(board):
    # Return True if every space on the board has been taken. Otherwise return False.
    for i in range(1, 10):
        if isSpaceFree(board, i):
            return False
    return True


def isBoardEmpty(board):
    # Return True if every space on the board has been taken. Otherwise return False.
    for i in range(1, 10):
        if not isSpaceFree(board, i):
            return False
    return True


def get_existing_game(player_id):
    return player_sessions.get(player_id, None)


def ask_for_input(player_id, send_message):
    send_message(player_id, message_strings.ask_for_input_string)


def send_rules(player_id, send_message):
    send_message(player_id, message_strings.rules_part1)
    send_message(player_id, message_strings.rules_part2)
    pass


def send_rules_option(player_id, send_message):
    send_message(player_id, message_strings.rules_option)


def send_language_option(player_id, send_message):
    language_option = '''
    If you speak English type EN.
    If you speak Russian type RU.
    '''
    send_message(player_id, language_option)


def ask_again(player_id, send_message):
    msg = random.choice(app.config['ASK_AGAIN_LIST'])
    send_message(player_id, msg)


def set_lang(message):
    if message and message.upper() == 'RU':
        import strings_ru as message_strings_local
    else:
        import strings_en as message_strings_local
    global message_strings
    message_strings = message_strings_local


def reset_player(player_id):
    player_session = player_sessions[player_id]
    player_sessions[player_id] = {'board': None,
                                  'play_first': not player_session.get('play_first', True),
                                  'lang': player_session.get('lang', 'EN')
                                  }


def make_computer_move(player_id, board, send_message):
    move = getComputerMove(board, 'O')
    makeMove(board, 'O', move)
    drawBoard(board, player_id, send_message)
    if isWinner(board, 'O'):
        send_message(player_id, message_strings.lose_message)
        reset_player(player_id)
        return False
    elif isBoardFull(board):
        send_message(player_id, message_strings.tie_message)
        reset_player(player_id)
        return False
    return True


def make_player_move(player_id, board, message, send_message):
    try:
        move = int(message)
    except:
        send_message(player_id, message_strings.valid_move_string)
        return False
    if move < 1 or move > 9:
        send_message(player_id, message_strings.valid_move_string)
        return False
    elif not isSpaceFree(board, move):
        send_message(player_id, message_strings.space_occupied)
        return False
    else:
        makeMove(board, 'X', move)
        drawBoard(board, player_id, send_message)
        if isWinner(board, 'X'):
            send_message(player_id, message_strings.win_message)
            reset_player(player_id)
            return False
        elif isBoardFull(board):
            send_message(player_id, message_strings.tie_message)
            reset_player(player_id)
            return False
    return True


def get_user_profile(player_id):
    payload = {'fields': 'first_name,locale',
               'access_token': os.environ['PAGE_ACCESS_TOKEN']}
    url = "https://graph.facebook.com/v2.6/{user_id:s}".format(user_id=player_id)
    resp = requests.post(url, params=payload)
    return resp.json()


def get_next_step(player_id, message, send_message):
    player_id = str(player_id)
    player_session = get_existing_game(player_id)
    app.logger.info('Saved session: {}'.format(player_session))

    board = None
    lang = None
    player_first = True
    if player_session:
        lang = player_session.get('lang', None)
        set_lang(lang)
        board = player_session.get('board', None)
        player_first = player_session.get('play_first', True)
    if not player_session or not board:
        if message.upper() != 'PLAY':
            ask_again(player_id, send_message)
            return
        if not board:
            app.logger.info('New board')
            newBoard = ['_'] * 10
            if not player_session:
                player_sessions[player_id] = {}
                player_sessions[player_id]['profile'] = get_user_profile(player_id)
                app.logger.info('New session')
                app.logger.info(player_session[player_id])
            player_sessions[player_id]['board'] = newBoard
            board = player_sessions[player_id]['board']
        print "new board = ", board
        print 'new player_session', player_sessions[player_id]
        if not lang:
            send_language_option(player_id, send_message)
            return
        if not player_first:
            make_computer_move(player_id, board, send_message)
    elif message.upper() == 'EN' or message.upper() == 'RU':
        player_session = get_existing_game(player_id)
        if not player_session:
            ask_again(player_id, send_message)
            return
        player_session['lang'] = message.upper()
        set_lang(message)
        send_rules_option(player_id, send_message)
    elif message.upper() == message_strings.rule_string:
        send_rules(player_id, send_message)
    else:

        if player_first or not isBoardEmpty(board):
            if not make_player_move(player_id, board, message, send_message):
                ask_again(player_id, send_message)
                return
            if not make_computer_move(player_id, board, send_message):
                ask_again(player_id, send_message)
                return
        else:
            if isBoardEmpty(board) and not make_computer_move(player_id, board, send_message):
                ask_again(player_id, send_message)
                return

    ask_for_input(player_id, send_message)
