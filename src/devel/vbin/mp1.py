# Multiprocessing example
# mp1.py  run mp2.py
from multiprocessing import Process,Pipe

def f(child_conn):
    msg = "Hello"
    child_conn.send(msg)
    child_conn.close()
