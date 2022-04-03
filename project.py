# Ricart & Agrawala
# Author: Magnus Karlson

import sys
import time
import random
from threading import Thread

if len(sys.argv) < 2 or int(sys.argv[1]) < 1:
    raise Exception("Number of processes must be atleast 1!")

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
        self.timestamp = 0
        self.start_p_countdown()

    def start_p_countdown(self):
        self.state = State.DONOTWANT
        self.countdown = random.randint(5, max_p_timeout)

    def start_cs_countdown(self):
        self.state = State.HELD
        self.countdown = random.randint(10, max_cs_timeout)

    def run(self):
        while True:
            if stopped: break

            time.sleep(1)
            if self.countdown == 0 or self.state not in [State.DONOTWANT, State.HELD]:
                continue
            
            self.countdown -= 1

            if self.countdown == 0:
                # Switch to wanted state
                if self.state == State.DONOTWANT:
                    self.state = State.WANTED
                    self.timestamp = time.time()
                    cs_access()

                # CS access has expired
                elif self.state == State.HELD:
                    self.start_p_countdown()
                    cs_access()


    def __str__(self):
        return self.name + ', ' + self.state

# Launches N amount of proccesses
for i in range(total):
    th = Process(f'P{i + 1}')
    th.start()
    processes.append(th)

# Checks for processes that are waiting for access
def cs_access():
    res = None
    for p in processes:
        # Exits when some process has CS access
        if p.state == State.HELD: return
        # Checks if there exists process with WANTED state and it has the lower timestamp
        if p.state == State.WANTED and (res == None or p.timestamp < res.timestamp):
            res = p
    # Grants cs access for process
    if res != None:
        res.start_cs_countdown()

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