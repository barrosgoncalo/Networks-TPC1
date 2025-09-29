import threading
import socket
import pickle
import os
import sys

# messages

GREETING = "Welcome to {} file server"
CLIENT_DISCONNECTED = "Client {} disconnected"

# errors

FILE_NOT_FOUND = "File not found"

# opcodes
RQQ_OPCODE = 1
DAT_OPCODE = 3
ACK_OPCODE = 4
ERR_OPCODE = 5

# block#
FIRST_BLOCK = 1
EMPTY = 0

# buffer size
bufferSize = 512

# local address
hostname = socket.gethostname()
local_addr = socket.gethostbyname(hostname)


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
    # métodos
    def getErrMsg(self):
        return self.errstring
    

def resetBlock():
    return 1

def sendDat(conn: socket.socket, msg: str, block_idx: int):
    dat_obj = Dat(FIRST_BLOCK, bufferSize, msg)
    packet = pickle.dumps(dat_obj)
    conn.send(packet)

def sendErr(conn: socket.socket, msg: str):
    err_obj = Err(msg)
    packet = pickle.dumps(err_obj)
    conn.send(packet)

def is_ack(packet):
    return packet.getOpcode() == ACK_OPCODE

def handle_client(conn: socket.socket, addrClient):

    msg = GREETING.format(local_addr)
    
    # create and send dat packet with the greeting message
    sendDat(conn, msg, FIRST_BLOCK)

    #wait until for te ACK
    conn.recv(bufferSize)

    while True:

        block_idx = resetBlock()

        enc_rqq = conn.recv(bufferSize)
        if not enc_rqq:
            print(CLIENT_DISCONNECTED.format(addrClient))
            conn.close()
            return
        packet = pickle.loads(enc_rqq)

        if(packet.getOpcode() == RQQ_OPCODE):

            block_idx = 0 # block index intancianted
            rqq_fileName = packet.getFileName()
            
            match rqq_fileName:
                case "":
                    block_idx = resetBlock()

                    dir_path = "."
                    dir_list = os.listdir(dir_path)
                    dir_list.sort(key = lambda s: sum(map(ord, s)))

                    for file_name in dir_list:
                        if os.path.isfile(os.path.join(dir_path, file_name)):

                            # Dat package with filename dispatch
                            sendDat(conn, file_name, block_idx)

                            # Ack package receival control
                            enc_ack = conn.recv(bufferSize)
                            packet = pickle.loads(enc_ack)
                            if not is_ack(packet):
                                conn.close()
                                break

                            block_idx += 1

                    # Send "sentinel" package
                    sentinel = Dat(block_idx, EMPTY, "")
                    conn.send(pickle.dumps(sentinel))

                case _:
                    block_idx = resetBlock()
                    
                    #check if the file exists ot not
                    if not os.path.exists(rqq_fileName):
                        sendErr(conn ,FILE_NOT_FOUND)
                        break

                    # open requested file to read
                    with open(rqq_fileName, "r") as file:
                        # read and send file data
                        while data := file.read(bufferSize):

                            # creating and sending packages Dat with read data
                            sendDat(conn, data, block_idx)

                            # Ack package receival control
                            enc_ack = conn.recv(bufferSize)
                            packet = pickle.loads(enc_ack)
                            if not is_ack(packet):
                                conn.close()
                                break

                            block_idx += 1 # block index updated to next block
                            
                        # Send "sentinel" package
                        sentinel = Dat(block_idx, EMPTY, "")
                        conn.send(pickle.dumps(sentinel))
                    
        

def main():

    serverPort = int(sys.argv[1])
    try:    
        TCPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCPServerSocket.bind(("", serverPort))
        print("Server is running")

    except:
        print("Unable to start server")

    while(True):
        TCPServerSocket.listen()
        conn, addrClient = TCPServerSocket.accept()
        tid = threading.Thread(target=handle_client, args=(conn, addrClient))
        tid.start()




main()