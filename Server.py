import threading
import socket
import pickle
import os

def handle_client():


def main():
    port = 20000
    buffer = 1024
    addrServer = "172.17.0.2"

    try:    
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((addrServer, port))
        print("Server is running")

    except:
        print("Unable to start server")

    while(True):
        conn, addrClient = server.accept()
        tid = threading.Thread(target=handle_client, args=(conn, ))
        tid.start



main()