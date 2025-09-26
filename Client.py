#imports
import sys
from socket import *
import pickle
import pathlib

# Constants
GET_NUM_ARGS = 2

RQQ_OPCODE = 1
DAT_OPCODE = 2
ACK_OPCODE = 3
ERR_OPCODE = 4


# Commands
GET = "get"
DIR = "dir"
END = "end"

# Errors
INVALID_NUM_ARGS = "Invalid number of arguments."
FILE_ALREADY_EXISTS = "File already exists locally."
FILE_NOT_FOUND_SERVER = "File wasn't found in server."
FILE_NOT_FOUND = "FILE NOT FOUND."

server_addr = sys.argv[1]
server_port = sys.argv[2]
bufferSize = 512

#Packages

class Packet:
    def __init__(self, opcode):
        self.opcode = opcode

class RRQ(Packet):
    def __init__(self, filename):
        super().__init__(RQQ_OPCODE)
        self.filename = filename

class DAT(Packet):
    def __init__(self, block, size, data):
        super().__init__(DAT_OPCODE)
        self.block = block
        self.size = size
        self.data = data

class ACK(Packet):
    def __init__(self, block):
        super().__init__(ACK_OPCODE)
        self.block = block

class ERR(Packet):
    def __init__(self, errstring):
        super().__init__(ERR_OPCODE)
        self.errstring = errstring

#end package classes/definition

def main():

    TCPClientSocket = socket(family=AF_INET, type=SOCK_STREAM)
    TCPClientSocket.connect((server_addr, server_port))

    comm = input()

    if comm == DIR:
        pass #NOT DONE

    elif comm == GET:
        #arguments
        remote_filename = sys.argv[1]
        local_filename = sys.argv[2]
        num_arguments = len(sys.argv) - 1

        #CHECK: Number of arguments
        if num_arguments != GET_NUM_ARGS: 
            print(INVALID_NUM_ARGS)
        #CHECK: File already exists on client
        try:
            open(local_filename, "rb")

        except FileNotFoundError:
            # file request to server
            file_request = pickle.dump(RRQ(remote_filename))
            TCPClientSocket.send(file_request)

            # data sent by server analysis/ writting local file
            with open(local_filename, "wb") as f:
                while True:
                    data = TCPClientSocket.recv(bufferSize)
                    if isinstance(data, DAT): print("error")
                    if not data: break
                    f.write(data)

            #CHECK: File doesn't exist on server 
            if (TCPClientSocket.recv(bufferSize)):
                print(FILE_NOT_FOUND_SERVER)
        
        else:
            print(FILE_ALREADY_EXISTS)

    elif comm == END:
        pass #NOT DONE

    else:
        print("Unknow command.")


main()