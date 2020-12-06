import subprocess, sys

DEF_CLIENTS = 5
client_quantity = 0
process_list = []
try:
    if '-c' in sys.argv:
        client_quantity = int(sys.argv[sys.argv.index('-c') + 1])

    else:
        client_quantity = DEF_CLIENTS
    if client_quantity > 10:
        raise ValueError

except IndexError:
    print('After "-c" you should sign a number of clients')
    sys.exit(1)

except ValueError:
    print('10 Max clients')

try:
    while True:
        command = input('Choose work command: start - start server-client connection, close - close windows,'
                        ' ever else key to quit   ')

        if command == 'start':
            process_list.append(subprocess.Popen('python3 server.py', shell=True)) #macos
            # process_list.append(subprocess.Popen('python3 server.py', creationflags=subprocess.CREATE_NEW_CONSOLE)) #win
            for window in range(client_quantity):
                process_list.append(subprocess.Popen('python3 client.py', shell=True)) #macos
                # process_list.append(subprocess.Popen('python3 client.py', creationflags=subprocess.CREATE_NEW_CONSOLE)) #win
        elif command == 'close':
            while process_list:
                to_delete = process_list.pop()
                to_delete.kill()

        else:
            break
finally:
    sys.exit(1)
