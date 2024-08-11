distance_accept = 70

offset_accept = 10

turn_forward = 8.5
turn_backward = 5.5

def checkDistance(distance):
    global distance_accept
    global offset_accept

    response = {
        'isAccept': False,
    }

    offset = abs(distance_accept - distance)

    if offset <= offset_accept:
        response['isAccept'] = True
    else:
        if distance < distance_accept:
            response['direction'] = 'backward'
        else:
            response['direction'] = 'forward'

    return response

def getRepeat(distance):
    global distance_accept
    global offset_accept
    global turn_forward
    global turn_backward

    offset = abs(distance_accept - distance)

    if distance < distance_accept:
        repeat = int(offset / turn_backward)
    else:
        repeat = int(offset / turn_forward)

    return repeat if repeat > 1 else 1