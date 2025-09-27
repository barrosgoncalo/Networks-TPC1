#imports
import sys
from socket import *
import pickle
import os
import time


# Constants
GET_NUM_ARGS = 2
FIRST_BLOCK_CODE = 1


# Errors
INVALID_NUM_ARGS = "Invalid number of arguments"
FILE_ALREADY_EXISTS = "File already exists locally"
FILE_NOT_FOUND = "File not found"

# prints
FILE_TRANSFER_COMPLETED = "File transfer completed"


# Arguments
server_addr = "172.17.0.2"
server_port = 20000
bufferSize = 512


# opcodes
RQQ_OPCODE = 1
DAT_OPCODE = 3
ACK_OPCODE = 4
ERR_OPCODE = 5


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
    def getErrString(self):
        return self.errstring




# main
def main():
    
    print("starting...")
    
    is_running = True
    while is_running:
        try:

            print(".", end=' ',flush=True)
            time.sleep(1)

            TCPClientSocket = socket(family=AF_INET, type=SOCK_STREAM)
            TCPClientSocket.connect((server_addr, server_port))
            
            # Server greeting message
            packet = pickle.loads(TCPClientSocket.recv(bufferSize))
            if(packet.getOpcode() == DAT_OPCODE):
                msg = packet.getData()
                print(msg)
                Ack_packet = Ack(FIRST_BLOCK_CODE)
                encoded_packet = pickle.dumps(Ack_packet)
                TCPClientSocket.send(encoded_packet)

            # arguments
            user_input = input().split(" ")
            cmd = user_input[0]

            match cmd:
                case "dir":
                    pass

                case "get":

                    remote_filename = cmd[1]
                    local_filename = cmd[2]

                    #CHECK: num of arguments
                    num_arguments = len(sys.argv) - 1
                    if num_arguments != GET_NUM_ARGS: 
                        print(INVALID_NUM_ARGS)

                    #CHECK: file already exists on client
                    try:
                        open(local_filename, "rb")

                    except FileNotFoundError:
                        # request to server
                        packet_rrq = pickle.dumps(Rrq(remote_filename))
                        TCPClientSocket.send(packet_rrq)

                        # data = first package DAT
                        packet_bytes = TCPClientSocket.recv(bufferSize)
                        
                        # remaining packages DAT sent by server analysis
                        # writting local file
                        with open(local_filename, "wb") as f:
                            packet = pickle.loads(packet_bytes)
                            error = False
                            while packet.getSize() and not error:
                                if packet.getOpcode() == DAT_OPCODE:
                                    f.write(packet.getData())
                                    packet = pickle.load(TCPClientSocket.recv(bufferSize))
                                else: # File doesn't exist on server
                                    os.remove(local_filename)
                                    print(FILE_NOT_FOUND)
                                    error = True

                    else: print(FILE_ALREADY_EXISTS)

                case "end":
                    pass #NOT DONE

                case _:
                    print("Unknow command.")

        except KeyboardInterrupt:
            print("")
            print("Exiting!")
            is_running = False
    print("Ending ")


main()