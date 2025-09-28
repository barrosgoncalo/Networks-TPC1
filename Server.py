import threading
import socket
import pickle
import os
import sys


# opcodes
RQQ_OPCODE = 1
DAT_OPCODE = 3
ACK_OPCODE = 4
ERR_OPCODE = 5

port = 20000
addrServer = "172.17.0.2"
bufferSize = 512


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


def handle_client(conn: socket.socket, addrClient):
    while True:
        msg = f"Welcome to {addrServer} file server"

        #send the gretting msg
        data_packet = Dat(1, bufferSize, msg)
        req = pickle.dumps(data_packet)
        conn.sendto(req, addrClient)

        #wait until for te ACK
        conn.recvfrom(bufferSize)

        print("rcv")
        

def main():

    try:    
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((addrServer, port))
        print("Server is running")

    except:
        print("Unable to start server")

    while(True):
        server.listen()
        conn, addrClient = server.accept()
        tid = threading.Thread(target=handle_client, args=(conn, addrClient))
        tid.start()

        # Read requests
        enc_data = conn.recv(bufferSize)
        packet = pickle.loads(enc_data)

        if(packet.getOpcode() == DAT_OPCODE):
            match packet.getFileName():
                case "":
                    end_file = False
                    while not end_file:
                        packet = conn.recv(bufferSize)
                case _:
                




main()