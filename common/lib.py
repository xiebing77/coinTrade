
def reserve_float(value, float_digits=0):
    value_str = str(value)
    value_list = value_str.split('.')
    new_value_str = '.'.join([value_list[0], value_list[1][0:float_digits]])
    return float(new_value_str)

