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
SUCCESSFUL_TRANSFER = "File transfer completed"


# Arguments
server_addr = "172.17.0.2"
server_port = 20001
bufferSize = 1024


# opcodes
RQQ_OPCODE = 1
DAT_OPCODE = 3
ACK_OPCODE = 4
ERR_OPCODE = 5


#Packages

# classe principal
class Packet:
    def _init_(self, opcode):
        self.opcode = opcode
    # métodos
    def getOpcode(self):
        return self.opcode


# extensões da classe Packet

class Rrq(Packet):
    def _init_(self, filename):
        super()._init_(RQQ_OPCODE)
        self.filename = filename
    # métodos
    def getFileName(self):
        return self.filename

class Dat(Packet):
    def _init_(self, block, size, data):
        super()._init_(DAT_OPCODE)
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
    def _init_(self, block):
        super()._init_(ACK_OPCODE)
        self.block = block
    # métdos
    def getBlock(self):
        return self.block

class Err(Packet):
    def _init_(self, errstring):
        super()._init_(ERR_OPCODE)
        self.errstring = errstring
    # métodos
    def getErrMsg(self):
        return self.errstring

# exceptions

class FileTransferError(Exception):
    pass

class FileNotFound(Exception):
    pass

# methods

def write_file(packet, file):
    opCode = packet.getOpcode();
    if opCode == DAT_OPCODE:
        file.write(packet.getData())
        file.flush()
    elif opCode == ERR_OPCODE:
        print(packet.getErrString)
    else: # File doesn't exist on server
        raise FileTransferError()
        
        
def resetBlock(block):
    block = 1


# main
def main():
    
    print("starting...")
    
    # Client connection to server
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

    running = True
    while running:
        try:
            # starting animation
            print(".", end=' ',flush=True)
            time.sleep(1)

            # arguments
            user_input = input().split(" ")
            cmd = user_input[0].upper()

            block_idx = 1

            match cmd:
                case "DIR":
                    #block index reset
                    resetBlock(block_idx)

                    Rrq_packet = Rrq("")
                    encoded_packet = pickle.dumps(Rrq_packet)
                    TCPClientSocket.send(encoded_packet)
                    
                    while True:
                        packet = pickle.loads(TCPClientSocket.recv(bufferSize))
                        if (packet.getSize() == 0): break

                        try:
                            print(packet.getData())
                            ack_obj = Ack(block_idx)
                            ack_packet = pickle.dumps(ack_obj)
                            TCPClientSocket.send(ack_packet)
                            block_idx += 1
                        except:
                            pass #exception to make

                case "GET":
                    #block index reset
                    resetBlock(block_idx)

                    remote_filename = user_input[1]
                    local_filename = user_input[2]

                    #CHECK: num of arguments
                    num_arguments = len(sys.argv) - 1
                    if num_arguments != GET_NUM_ARGS: 
                        print(INVALID_NUM_ARGS)

                    #CHECK: file already exists on client
                    if not os.path.exists(local_filename):
                        # RRQ package dispatch
                        packet_rrq = pickle.dumps(Rrq(remote_filename))
                        TCPClientSocket.send(packet_rrq)
                        
                        # remaining packages DAT sent by server analysis
                        # writting local file
                        with open(local_filename, "w") as file:
                            while True:
                                try:
                                    enc_packet = TCPClientSocket.recv(bufferSize)
                                    packet = pickle.loads(enc_packet)

                                    if packet.getSize() == 0: break
                                    write_file(packet, file)

                                    ackPacket = Ack(block_idx)
                                    packet = pickle.dumps(ackPacket)
                                    TCPClientSocket.send(packet)

                                except FileTransferError: # how are we meant to treat it???
                                    # The expected block number of a DAT or ACK packet is incorrect.
                                    # There is a protocol error (an unexpected packet type is received).
                                    os.remove(local_filename)
                                    print(FILE_NOT_FOUND)
                                    error = True
                                
                                except EOFError:
                                    TCPClientSocket.close()
                                    sys.exit()

                        print(SUCCESSFUL_TRANSFER)


                    else: print(FILE_ALREADY_EXISTS)



                case "END":
                    print("Exiting!")
                    running = False

                case _:
                    print("Unknow command.")

        except KeyboardInterrupt:
            print("")
            print("Exiting!")
            running = False
    print("Ending ")


main()