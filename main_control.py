import asyncio
import socket
import json
import functools
INTERACT_1 = {1: 'See available Users.', 2: 'Connect to User.', 3: 'My Profile', 4: 'See/Modify shared files.',
              5: 'Exit.'}
INTERACT_2 = {1: 'Get Directory List.', 2: 'Download File.', 3: 'Back.'}
LANG = ['DIRL', 'GETF', 'GET', 'PUS', 'RSM', 'CNL']
target = ('<broadcast>',20000)
DIRECTORY_LIST = {'ssp_pdl.mp4', 'Rexa_bey.exe', 'lone_book.pdf'}
SERVER_ADDRESS = ('localhost', 10000)
AVAILABLE_NODES = dict()
NODE_DIRECTORIES = dict()
event_loop = asyncio.get_event_loop()
lock = asyncio.Lock()
MY_DETAILS = dict()

'''root = Tk()
root.title("LAN SHARE")
Label(root, text='Username').grid(row=0, column=0, sticky=W)
Entry(root, width=50).grid(row=0, column=1)
Button(root, text='Save').grid(row=0, column=8)
root.mainloop()'''



with open('config.json', 'r+') as f:
    my_details = json.load(f)
    print(my_details)
if my_details["name"] == '':
    name = input('Choose a username: ')
    my_details["name"] = name
    with open('config.json', 'w') as f:
        json.dump(my_details, f)
    MY_DETAILS = my_details
else:
    MY_DETAILS = my_details


def join(x, y):
    return x+'-'+y


def get_answer(p):
    if p == 'IAM':
        return 'WHO'


class BroadcastProtocol:
    def __init__(self, loop):
        self.loop = loop
        self.LANG = ['IOPEN', 'ROPEN', 'CLOSE', 'GLIST', 'TLIST']

    def connection_made(self, transport):
        self.transport = transport
        sock = transport.get_extra_info("socket")
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.broadcast('IOPEN#:#'+MY_DETAILS['name'])

    def datagram_received(self, data, addr):
        global MY_DETAILS
        try:
            lang, value = data.decode().split('#:#')
            if value != MY_DETAILS['name']:
                if lang == self.LANG[0]:
                    AVAILABLE_NODES.update({addr[0]: value})
                    self.transport.sendto(('ROPEN#:#'+MY_DETAILS['name']).encode(), addr)
                elif lang == self.LANG[1]:
                    if not AVAILABLE_NODES[addr[0]]:
                        AVAILABLE_NODES.update({addr[0]: value})
                    self.transport.sendto(("GLIST#:#"+str(DIRECTORY_LIST)).encode(), addr)
                elif lang == self.LANG[2]:
                    if AVAILABLE_NODES[addr[0]]:
                        del AVAILABLE_NODES[addr[0]]
                elif lang == self.LANG[3]:
                    NODE_DIRECTORIES.update({addr[0]: value})
            else:
                with open('config.json', 'r+')as f:
                    data = json.load(f)
                data["IP address"] = addr[0]
                with open('config.json', 'w') as f:
                    json.dump(data, f)
                MY_DETAILS = data
        except ValueError:
            print('Received Datagram is useless..')
        print(AVAILABLE_NODES)
        print(NODE_DIRECTORIES)

    def stop(self):
        self.broadcast('CLOSE#:#pksharmapokhrel')
        print('Closing Broadcasting.')
        self.transport.close()

    def connection_lost(self, exc):
        data = dict()
        with open('remote_node_details.json', 'w') as l:
            json.dump(data, l)
        print('bserver connection lost.')

    def broadcast(self, msg):
        print('broadcasting : ', msg)
        self.transport.sendto(msg.encode(), ('<broadcast>', 9000))

async def get_input():
    return input('$$->')


async def start_main(s, bs, loop):
    task = loop.create_task(get_input())
    for i in INTERACT_1:
        print(i, INTERACT_1[i])
    x = await task
    print(x)
    if x == '1':
        print(AVAILABLE_NODES)
    elif x == '2':
        task_0 = loop.create_task(get_input())
        p = await task_0
        print(p)
        task1 = loop.create_task(tcp_echo_client(p))
        result = await task1
        if result is not None:
            print('Work with server ', result, 'is done')
    elif x == '3':
        print(MY_DETAILS)
    elif x == '4':
        l = ['See', 'Add', 'remove', 'back']
        while True:
            for i in range(4):
                print(i, l[i-1])
            task_1 = loop.create_task(get_input())
            y = await task_1
            if y == '1':
                print(DIRECTORY_LIST)
            elif y == '2':
                task_2 = loop.create_task(get_input())
                p = await task_2
                if p not in DIRECTORY_LIST.keys():
                    DIRECTORY_LIST.update({p: "some mb"})
                else:
                    print('File already present')
            elif y == '3':
                task_3 = loop.create_task(get_input())
                p = await task_3
                if p in DIRECTORY_LIST.keys():
                    del DIRECTORY_LIST[p]
                else:
                    print('File not present')
            elif y == '4':
                break
    elif x == '5':
        bs[1].stop()
        s.close()
    if x != '5':
        await start_main(s, bs, loop)

async def handle_client(reader, writer):
    address = writer.get_extra_info('peername')
    print('Client accepted :', address)
    while True:
        data = await reader.read(128)
        if data:
            print('received {!r}'.format(data))
            data = data.decode()
            if data[:4] == LANG[0]:
                writer.write(str(DIRECTORY_LIST).encode())
            elif data[:4] == LANG[1]:
                f = open(data[5:], 'rb')
                data = f.read(1024)
                print('Sending File.')
                g = 0
                while data:
                    print(str(g)+repr(data))
                    writer.write(data)
                    g = g + 1024
                    data = f.read(1024)
                    if g/1024 == 500:
                        await writer.drain()
                        g = 0
                f.close()
            await writer.drain()
            print('Done Sending..')
        else:
            print('Closing....')
            writer.close()
            return

async def tcp_echo_client(dest_ip):
    reader, writer = await asyncio.open_connection(dest_ip, 10000)
    print(reader)
    print(writer)
    while reader and writer:
        for i in INTERACT_2:
            print(i, INTERACT_2[i])
        task = event_loop.create_task(get_input())
        x = await task
        if x == '1':
            print('-> Requesting Directory List..')
            writer.write('DIRL'.encode())
            data = (await reader.read(1000)).decode()
            print(data)
        elif x == '2':
            print('-> Requesting a File..')
            task_1 = event_loop.create_task(get_input())
            fname = await task_1
            rq = 'GETF-'+fname
            writer.write(rq.encode())
            f1 = open('new11.mp4', 'wb')
            g = 0
            while True:
                data = await reader.read(1024)
                g = g + 1
                print('r'+str(g)+repr(data))
                print(len(data))
                f1.write(data)
                if len(data) < 1024:
                    break
            print('Downloading Complete')
            f1.close()
        elif x == '3':
            break

    writer.close()
    return writer.get_extra_info('peername')


factory = asyncio.start_server(handle_client, *SERVER_ADDRESS)
print('starting up on {} port {}'.format(*SERVER_ADDRESS))
coro = event_loop.create_datagram_endpoint(lambda: BroadcastProtocol(event_loop), local_addr=('0.0.0.0', 9000))
server = event_loop.run_until_complete(factory)
bserver = event_loop.run_until_complete(coro)
input_loop = functools.partial(start_main, server, bserver, event_loop)


try:
    event_loop.run_until_complete(start_main(server, bserver, event_loop))
except KeyboardInterrupt:
    pass
finally:
    print('closing server')
    event_loop.run_until_complete(server.wait_closed())
    print('closing event loop')
    event_loop.close()
