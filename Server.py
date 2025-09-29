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
        return self.filename

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
    
def resetBlock(block):
    block = 1

def handle_client(conn: socket.socket, addrClient):

    block_idx = 0

    msg = f"Welcome to {addrServer} file server"
    
    #send the gretting msg
    dat_packet = Dat(1, bufferSize, msg)
    req = pickle.dumps(dat_packet)
    conn.send(req)

    #wait until for te ACK
    conn.recv(bufferSize)

    while True:

        enc_data = conn.recv(bufferSize)
        packet = pickle.loads(enc_data)
        end_file = False

        if(packet.getOpcode() == RQQ_OPCODE):
            resetBlock(block_idx)

            print(packet.getFileName())

            match packet.getFileName():
                case "":
                    dir_path = "."
                    dir_list = os.listdir(dir_path)
                    dir_list.sort(key = lambda s: sum(map(ord, s)))
                    print(dir_list)

                    for file_name in dir_list:
                        if os.path.isfile(os.path.join(dir_path, file_name)):
                            dat_obj = Dat(block_idx, bufferSize, file_name)
                            packet = pickle.dumps(dat_obj)
                            conn.send(packet)
                            #Ack package receival
                            conn.recv(bufferSize)
                            block_idx += 1
                    #Send "sentinel" package
                    conn.send(pickle.dumps(Dat(1, 0, "")))

                case _:
                    resetBlock(block_idx)
                    with open(packet.getFileName(), "r") as file:
                        while data := file.read(bufferSize):

                            dat_packet = Dat(block_idx, bufferSize, data)

                            req = pickle.dumps(dat_packet)
                            conn.send(req)

                            #ack block
                            conn.recv(bufferSize)
                            block_idx += 1
                        sentinel = Dat(block_idx, 0, "")
                        conn.send(pickle.dumps(sentinel))
        

def main():

    serverPort = int(sys.argv[1])
    try:    
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("", serverPort))
        print("Server is running")

    except:
        print("Unable to start server")

    while(True):
        server.listen()
        conn, addrClient = server.accept()
        tid = threading.Thread(target=handle_client, args=(conn, addrClient))
        tid.start()
                




main()