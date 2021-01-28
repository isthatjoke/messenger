import dis


class ClientVerifier(type):
    """
    meta class to check child class methods
    """
    def __init__(self, name, bases, dict):

        methods_lst = []
        func_lst = []
        for el in dict:
            try:
                instruction_bytes = dis.get_instructions(dict[el])
            except TypeError:
                pass
            else:
                for value in instruction_bytes:
                    if value.opname == 'LOAD_METHOD':
                        if value.argval not in methods_lst:
                            methods_lst.append(value.argval)

                    if value.opname == 'LOAD_GLOBAL':
                        if value.argval not in func_lst:
                            func_lst.append(value.argval)

        for method in ('accept', 'listen', 'socket'):
            if method in methods_lst:
                raise TypeError('error method in client1 class')

        if 'seng_msg' in func_lst or 'receive_msg' in func_lst:
            pass
        else:
            raise TypeError("there's no socket functions in class")

        super().__init__(name, bases, dict)


if __name__ == '__main__':
    pass
