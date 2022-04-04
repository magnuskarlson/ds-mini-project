# Ricart & Agrawala
# Author: Magnus Karlson

from threading import Thread
import time
import socket
import sys
import random

if len(sys.argv) < 2 or int(sys.argv[1]) < 1:
    exit("Number of processes must be atleast 1!")

max_p_timeout = 5
max_cs_timeout = 10
total = int(sys.argv[1])
processes = []

HOST = '127.0.0.1'
PORT = 17000

class State:
    WANTED = 'WANTED'
    HELD = 'HELD'
    DONOTWANT = 'DO-NOT-WANT'

class Process(Thread):
    def __init__(self, index, total):
        Thread.__init__(self)
        self.index = index
        self.total = total
        self.timestamp = 0
        self.queue = []
        self.waitsResponse = []
        self.start_p_countdown()
        Thread(target=self.launch_server).start()

    def start_p_countdown(self):
        self.state = State.DONOTWANT
        self.countdown = random.randint(5, max_p_timeout)

    def start_cs_countdown(self):
        self.state = State.HELD
        self.countdown = random.randint(10, max_cs_timeout)

    # Process server listening requests
    def launch_server(self):
        s = socket.socket()
        s.bind((HOST, PORT + self.index))
        s.listen(self.total)
        while True:
            con, addr = s.accept()
            action, index, timestamp = con.recv(1024).decode().split('_')
            index = int(index)
            timestamp = int(timestamp)

            if action == 'CSASK':
                # Process doesn't want to access cs
                if self.state == State.DONOTWANT:
                    con.send('ok'.encode())
                # Process itself wants to access critical section
                elif self.state == State.WANTED:
                    # Req process has lower timestamp
                    if timestamp < self.timestamp:
                        con.send('ok'.encode())
                    # Queue current process
                    else:
                        con.send('notok'.encode())
                        self.queue.append(index)
                # Process is accessing cs, queue req
                elif self.state == State.HELD:
                    con.send('notok'.encode())
                    self.queue.append(index)
            
            elif action == 'CSEND':
                self.waitsResponse.remove(index)
                if len(self.waitsResponse) == 0:
                    self.start_cs_countdown()

    # RPC requests
    def send_access_req(self):
        for i in range(total):
            if i == self.index: continue
            # creates connection
            s = socket.socket()
            s.connect((HOST, PORT + i))
            s.send(f'CSASK_{self.index}_{self.timestamp}'.encode())

            # gets response
            res = s.recv(1024).decode()

            # stores processes, what response it waits
            if res != 'ok':
                self.waitsResponse.append(i)

            # closes connection
            s.close()

        if len(self.waitsResponse) == 0:
            self.start_cs_countdown()

    def send_cs_finished(self):
        for i in self.queue:
            s = socket.socket()
            s.connect((HOST, PORT + i))
            s.send(f'CSEND_{self.index}_{self.timestamp}'.encode())
            s.close()

        self.queue = []

    def run(self):
        while True:
            time.sleep(1)
            self.timestamp += 1

            if self.countdown == 0 or self.state not in [State.DONOTWANT, State.HELD]:
                continue

            self.countdown -= 1
            if self.countdown == 0:
                if self.state == State.DONOTWANT:
                    self.state = State.WANTED
                    self.send_access_req()
                elif self.state == State.HELD:
                    self.start_p_countdown()
                    self.send_cs_finished()

    def __str__(self):
        return f'P{self.index + 1}, {self.state}'

for i in range(total):
    time.sleep(0.05) # small delay between threads, so they don't do everything at the exact same time
    p = Process(i, total)
    processes.append(p)
    p.start()

while True:
    msg = input("Enter command (list | info | time-cs | time-p | exit): ")
    parts = msg.split(' ')
    cmd = parts[0].lower()
    param = parts[1] if len(parts) > 1 else ''

    if cmd == 'list':
        for p in processes:
            print(p)

    elif cmd == 'info':
        print(f'p-max-timeout {max_p_timeout}, cs-max-timeout {max_cs_timeout}, processes {len(processes)}')

    elif cmd == 'time-cs':
        if not param.isdigit() or int(param) < 10:
            print('Invalid CS timeout!')
            continue
        max_cs_timeout = int(param)

    elif cmd == 'time-p':
        if not param.isdigit() or int(param) < 5:
            print('Invalid p timeout!')
            continue
        max_p_timeout = int(param)

    elif cmd == 'exit':
        for p in processes:
            p.join()
        break


