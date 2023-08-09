import time

if time.sleep(5):
    print('hello')

    if left_point != -1: left_lt.append(left_point)
    if right_point != -1:right_lt.append(right_point)

    #############
    if right_point != -1 and left_point != -1:
        if len(left_lt) > 8:
            dis = np.abs(left_point - left_lt[-8])
            if dis > 5:
                left_point -= lane_width//2
                left_lt.pop(-1)
                # left_lt.append(left_point)

        if len(right_lt) > 8:
            dis = np.abs(right_point - right_lt[-8])
            if dis > 7:
                right_point += lane_width//2
                right_lt.pop(0)
                # right_lt.append(right_point)
    #############
    if left_point != -1 and right_point == -1:
        if len(left_lt) > 8:
            dis = np.abs(left_point - left_lt[-8])
            if dis > 5:
                left_point -= lane_width//2
                left_lt.pop(-1)
                # left_lt.append(left_point)
        right_point = left_point + lane_width
    ############
    if right_point != -1 and left_point == -1:
        if len(right_lt) > 8:
            dis = np.abs(right_point - right_lt[-8])
            if dis > 6:
                if right_point - right_lt[-8] > 0:
                    right_point += lane_width//2
                    right_lt.pop(0)
                    # right_lt.append(right_point)
        left_point = right_point - lane_width

    ################
    if points:
        if right_point == -1 and left_point == -1:
            left_point, right_point = points[-1]
            print('hal9')
            print('hi')
