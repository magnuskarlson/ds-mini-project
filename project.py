import time
import random
from threading import Thread

# Process states
class State:
    WANTED = 'WANTED'
    HELD = 'HELD'
    DONOTWANT = 'DO-NOT-WANT'

# Process with critical section access
cs_process = ''
max_timeout = 5

class Process(Thread):
    def __init__(self, name):
        Thread.__init__(self)
        self.name = name
        self.state = State.DONOTWANT
        self.set_timeout()

    def set_timeout(self):
        self.stateTimeout = random.randint(5, max_timeout)
    
    def run(self):
        while True:
            time.sleep(1)
            self.stateTimeout -= 1
            if self.stateTimeout == 0:
                if self.state == State.DONOTWANT:
                    self.state = State.WANTED
                self.set_timeout()


    def __str__(self):
        return self.name + ', ' + self.state

class Parent:
    def __init__(self, n):
        self.procs = []
        for i in range(n):
            th = Process(f'P{i + 1}')
            th.start()
            self.procs.append(th)

    def status(self):
        for p in self.procs:
            print(p)


p = Parent(10)

while True:
    msg = input("Enter command (list): ")
    parts = msg.split(' ')
    cmd = parts[0].lower()
    param = parts[1] if len(parts) > 1 else ''

    if cmd == 'list':
        p.status()

    elif cmd == 'exit':
        break