# opcodes
RQQ_OPCODE = 1
DAT_OPCODE = 2
ACK_OPCODE = 3
ERR_OPCODE = 4


#Packages

# classe principal
class Packet:
    def __init__(self, opcode):
        self.opcode = opcode
    # métodos
    def getOpcode(self):
        return self.opcode

# extensões da classe Packet
class Rrq(Packet):
    def __init__(self, filename):
        super().__init__(RQQ_OPCODE)
        self.filename = filename
    # métodos
    def getFileName(self):
        self.filename

class Dat(Packet):
    def __init__(self, block, size, data):
        super().__init__(DAT_OPCODE)
        self.block = block
        self.size = size
        self.data = data
    # métodos
    def getBlock(self):
        return self.block
    def getSize(self):
        return self.size
    def getData(self):
        return self.data

class Ack(Packet):
    def __init__(self, block):
        super().__init__(ACK_OPCODE)
        self.block = block
    # métdos
    def getBlock(self):
        return self.block

class Err(Packet):
    def __init__(self, errstring):
        super().__init__(ERR_OPCODE)
        self.errstring = errstring
    def getErrString(self):
        return self.errstring
    
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
        tid.start()



main()