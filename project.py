# Ricart & Agrawala
# Author: Magnus Karlson

import sys
import time
import random
from threading import Thread

if len(sys.argv) < 2 or int(sys.argv[1]) < 1:
    exit("Number of processes must be atleast 1!")

total = int(sys.argv[1])
max_p_timeout = 5
max_cs_timeout = 10
processes = []  # Currently registered processes
stopped = False

# Process states
class State:
    WANTED = 'WANTED'
    HELD = 'HELD'
    DONOTWANT = 'DO-NOT-WANT'

# Process class
class Process(Thread):
    def __init__(self, name):
        Thread.__init__(self)
        self.name = name
        self.timestamp = 0      # Lamport timestamp
        self.queue = []
        self.waitsResponse = []
        self.start_p_countdown()

    def start_p_countdown(self):
        self.state = State.DONOTWANT
        self.countdown = random.randint(5, max_p_timeout)

    def start_cs_countdown(self):
        self.state = State.HELD
        self.countdown = random.randint(10, max_cs_timeout)

    # Called by other process
    def RPC_ask_access(self, p, timestamp):
        # Process doesn't want to access cs
        if self.state == State.DONOTWANT:
            return 'ok'
        
        # Process itself wants to access critical section
        elif self.state == State.WANTED:
            # Req process has lower timestamp
            if timestamp < self.timestamp:
                return 'ok'
            # Queue current process
            else:
                self.queue.append(p)
                return None
        # Process is accessing cs, queue req
        elif self.state == State.HELD:
            self.queue.append(p)
            return None
    
    # Called by other processes to tell that, it has recieved one more approval
    # RPC reciever for telling
    def RPC_send_cs_finished(self, p):
        self.waitsResponse.remove(p)
        if len(self.waitsResponse) == 0:
            self.start_cs_countdown()
    
    # Process asks other processes for access
    # RPC sends access request to other processes
    def send_access_req(self):
        # Sends message to every other process
        # If everyones response isn't ok, access isn't given
        for p in processes:
            if p == self: continue
            res = p.RPC_ask_access(self, self.timestamp)
            if res != 'ok':
                self.waitsResponse.append(p)
        # Give access to cs
        if len(self.waitsResponse) == 0:
            self.start_cs_countdown()

    
    # Sends message that are waiting for response, that it's finished accessing cs
    # RPC sends message to other processes
    def send_cs_finished(self):
        for p in self.queue:
            p.RPC_send_cs_finished(self)
        self.queue = []

    def run(self):
        while True:
            if stopped: break

            time.sleep(1)
            self.timestamp += 1

            if self.countdown == 0 or self.state not in [State.DONOTWANT, State.HELD]:
                continue
            
            self.countdown -= 1

            if self.countdown == 0:
                # Switch to wanted state
                if self.state == State.DONOTWANT:
                    self.state = State.WANTED
                    self.send_access_req()

                # CS access has expired
                elif self.state == State.HELD:
                    self.start_p_countdown()
                    self.send_cs_finished()


    def __str__(self):
        return self.name + ', ' + self.state

# Launches N amount of proccesses
for i in range(total):
    th = Process(f'P{i + 1}')
    th.start()
    processes.append(th)

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
        stopped = True
        break