def f2i(float_value):
    if float_value < 0:
        float_value = abs(float_value)
        sign_flag = 1
    else:
        sign_flag = 0
    if float_value > 1:
        float_value -= int(float_value)
    idx = 1
    res = 0
    while float_value != 0:
        float_value = float_value * 2.0
        if float_value > 1.0:
            res |= pow(2, 31 - idx)
            float_value -= 1.0
        if idx == 31:
            res |= 1
            break
        idx += 1
    if sign_flag == 1:
        res = pow(2, 32) - res
    return res

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        input_value = float(sys.argv[1])
        res = f2i(input_value)
        my_convt = int(abs(input_value) * (pow(2.0, 31)))
        if input_value < 0:
            my_convt = pow(2, 32) - my_convt
            print(f'input = {input_value}, output = 0x{res:8x} = {res}, '
                f'my_convt = 0x{my_convt:8x} = {my_convt}')
