def human_format(num: int):
    """
    This function will convert long number to human read able format
    :param num: The long number
    :return: The human read able format
    :return: The human read able format
    """
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])
