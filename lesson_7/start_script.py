import subprocess, sys, os, time

DEF_CLIENTS = 2
client_quantity = 0
process_list = []
# with open("start_server_clients.command", "w") as f:
#     f.write("#!/bin/sh\npython3 client_oop.py\n")
# os.chmod('start_server_clients.command', os.stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH)

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
        cmd = input('Choose work command: start - start server-client connection, close - close windows,'
                    ' ever else key to quit   ')

        if cmd == 'start':
            # process_list.append(subprocess.Popen('python3 server_oop.py', shell=True)) #macos
            # process_list.append(subprocess.Popen('python3 server_oop.py', creationflags=subprocess.CREATE_NEW_CONSOLE)) #win
            process_list.append(subprocess.Popen(['/usr/bin/open', '-n', '-a', 'Terminal',
                                                  'start_server.command'], shell=False)) #macos
            time.sleep(1)

            for window in range(3):
                process_list.append(subprocess.Popen(['/usr/bin/open', '-n', '-a', 'Terminal',
                                                      'start_clients.command'], shell=False))  #macos
                # process_list.append(subprocess.Popen('python3 client_oop.py -m listener', creationflags=subprocess.CREATE_NEW_CONSOLE)) #win
            for window in range(2):
                process_list.append(subprocess.Popen(['/usr/bin/open', '-n', '-a', 'Terminal',
                                                      'start_client_sender.command'], shell=False))
                # process_list.append(subprocess.Popen('python3 client_oop.py -m sender', creationflags=subprocess.CREATE_NEW_CONSOLE)) #win
        elif cmd == 'close':
            while process_list:
                to_delete = process_list.pop()
                to_delete.kill()

        else:
            break
finally:
    sys.exit(1)
