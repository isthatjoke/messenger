
class IncorrectData(BaseException):

    def __str__(self):
        return 'received incorrect data'


class IncorrectType(BaseException):

    def __str__(self):
        return 'incorrect type'


class IncorrectDataToDecode(BaseException):

    def __str__(self):
        return 'incorrect data to decode. must be bytes'


class ClientError(BaseException):

    def __str__(self):
        return 'fuckup with starting client1'

