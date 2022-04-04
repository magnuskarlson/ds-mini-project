# Distributed Systems | Mini Project 1
## Magnus Karlson

## Usage
* py project.py (number of processes)       | Uses simple class calling between processes
* py project-rpc.py (number of processes)   | Uses sockets between processes to send requests to them

**Example**   
* py project.py 7  
* py project-rpc.py 7

## Commands
* list - shows processes and their current state
* info - shows max cs timeout, max p timeout, number of processes
* time-cs (number) - change max possible timeout for critical section
* time-p (number) - change max possible timeout for state

