from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
import sys, json
from additionals.settings import DEFAULT_PORT, PACK_CAPACITY, MAX_CONNECTIONS, ENCODING
from additionals.utils import send_msg, receive_msg


def close(sock):
    sock.shutdown(SHUT_RDWR)


def check_client_presence(message):
    if 'action' in message and message['action'] == 'presence' and 'time' in message \
            and 'user' in message and message['user']['account_name'] == 'Guest':
        return {'response': 200}
    return {'response': 400, 'ERROR': 'Bad Request'}


def main():

    try:
        if '-help' in sys.argv:
            print("""
                To use this script u should sign 2 params:
                -a ip-address
                -p port
                example:
                server.py -a 127.0.0.1 -p 9999
            """)
            sys.exit(0)
    finally:
        pass

    try:
        if '-a' in sys.argv:
            ip_addr = sys.argv[sys.argv.index('-a') + 1]
        else:
            ip_addr = ''
    except IndexError:
        print('u should sign ip address')
        sys.exit(1)

    try:
        if '-p' in sys.argv:
            port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            port = DEFAULT_PORT
        if 65535 < port < 1024:
            raise ValueError
    except IndexError:
        print('u should sign port')
        sys.exit(1)
    except ValueError:
        print('port must be in range 1024 - 65535')
        sys.exit(1)

    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind((ip_addr, port))
    sock.listen(MAX_CONNECTIONS)

    while True:
        client, addr = sock.accept()
        try:
            message = receive_msg(client)
            response = check_client_presence(message)
            send_msg(client, response)
            client.close()
        except (ValueError, json.JSONDecodeError):
            print('incorrect message has been received')
            client.close()
            close(sock)


if __name__ == '__main__':
    main()

