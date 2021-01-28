def check_ip(ip):
    """
    check if ip address is correct
    :param ip: str ip address
    :return: bool, true if ip is correct
    """
    for el in ip:
        if el.isdigit() or el == '.':
            pass
        else:
            return False
    return True


def check_first_octet(data):
    """
    check first octet of ip address
    :param data: int
    :return: bool
    """
    if 1 <= int(data) < 256:
        return True
    else:
        return False


def check_second_third_octets(data):
    """
    check second and third octets of ip address
    :param data: int
    :return: bool
    """
    if 0 <= int(data) < 256:
        return True
    else:
        return False


def check_forth_octet(data):
    """
    check forth octet of ip address
    :param data: int
    :return: bool
    """
    if 0 <= int(data) < 255:
        return True
    else:
        return False