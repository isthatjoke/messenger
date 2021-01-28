def check_ip(ip):
    for el in ip:
        if el.isdigit() or el == '.':
            pass
        else:
            return False
    return True


def check_first_octet(data):
    if 1 <= int(data) < 256:
        return True
    else:
        return False


def check_two_three_octets(data):
    if 0 <= int(data) < 256:
        return True
    else:
        return False


def check_forth_octet(data):
    if 0 <= int(data) < 255:
        return True
    else:
        return False