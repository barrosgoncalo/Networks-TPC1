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

# extensões da classe Packet
class Rrq(Packet):
    def __init__(self, filename):
        super().__init__(RQQ_OPCODE)
        self.filename = filename

class Dat(Packet):
    def __init__(self, block, size, data):
        super().__init__(DAT_OPCODE)
        self.block = block
        self.size = size
        self.data = data
    # métodos
    def getSize(self):
        return self.size
    def getData(self):
        return self.data

class Ack(Packet):
    def __init__(self, block):
        super().__init__(ACK_OPCODE)
        self.block = block

class Err(Packet):
    def __init__(self, errstring):
        super().__init__(ERR_OPCODE)
        self.errstring = errstring