offset_accept = 50

turn_right = 19
turn_left = 7

def checkOffset(offset_x):
    global offset_accept

    response = {
        'isAccept': False,
    }

    offset = abs(offset_x)

    if offset <= offset_accept:
        response['isAccept'] = True
    else:
        if offset_x > 0:
            response['direction'] = 'right'
        else:
            response['direction'] = 'left'

    return response

def getRepeat(offset_x):
    global offset_accept
    global turn_left
    global turn_right

    offset = abs(offset_x)

    if offset_x > 0:
        repeat = int(offset / turn_right)
    else:
        repeat = int(offset / turn_left)

    return repeat if repeat > 1 else 1
