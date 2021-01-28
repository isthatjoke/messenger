import dis


class ServerVerifier(type):
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

        if 'connect' in methods_lst:
            raise TypeError('error method in client1 class')

        if not ('AF_INET' in methods_lst and 'SOCK_STREAM' in methods_lst):
            pass
        else:
            raise TypeError('incorrect initialisation of socket')

        super().__init__(name, bases, dict)


if __name__ == '__main__':
    pass
