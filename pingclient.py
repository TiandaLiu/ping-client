import threading
import socket
import sys
import os
import struct
import time

class PingClient:

    def __init__(self, server_ip, server_port, count, period, timeout):
        self.serverAddress = (server_ip, server_port)
        self.count = count
        self.period = period
        self.timeout = timeout

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(1)

        self.sendCount = 0
        self.recvCount = 0
        self.starttime = 0
        self.rtts = []
    
    def main(self):

        # start a thread
        t = threading.Timer(self.period//1000, self.sendMessage)
        t.start()
        self.starttime = int(time.time() * 1000)
        print("PING {}".format(self.serverAddress[0]))

        flag = 0
        lastSendTime = 0
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)
        while True:
            # check the last send
            if self.sendCount == self.count and flag == 0:
                flag = 1
                lastSendTime = time.time()
            if flag == 1:
                if time.time() - lastSendTime > self.timeout//1000:
                    # print("Finished")
                    self.printStats()
                    break
            # listening message from server
            try:
                recvMessage, serverAddress = self.sock.recvfrom(2048)
                if self.checkValid(recvMessage) and not self.expired(recvMessage):
                    self.recvCount += 1
                    timeElapse = int(time.time() * 1000) - int.from_bytes(recvMessage[-6:], byteorder='big')
                    self.rtts.append(timeElapse)
                    seqno = struct.unpack("!H", recvMessage[6:8])
                    print("PONG {0}: seq={1} time={2}ms".format(serverAddress[0], seqno[0], timeElapse))
            except OSError:
                pass
    
    # send message to server
    def sendMessage(self):
        message = self.generateMessage()
        self.sock.sendto(message, self.serverAddress)
        self.sendCount += 1
        if self.sendCount == self.count:
            return
        t = threading.Timer(self.period//1000, self.sendMessage)
        t.start()

    # check type and checksum
    def checkValid(self, message): 
        if int.from_bytes(message[:1], byteorder='big') != 0:
            return False
        checksum = self.generateChecksum(message)
        if checksum != 0:
            print("Checksum verification failed for echo reply seqno={}".format(struct.unpack("!H", message[6:8])[0]))
            return False
        return True
    
    # check timestamp
    def expired(self, message):
        currtime = int(time.time() * 1000)
        timestamp = int.from_bytes(message[-6:], byteorder='big')
        if currtime - timestamp > self.timeout:
            return True
        return False
    
    # pack message
    def generateMessage(self):
        timestamp = int(time.time()*1000).to_bytes(6, byteorder='big')
        type = b'\x08'
        code = b'\x00'
        identifier = struct.pack("!H", (os.getpid()%65535))
        seqno = struct.pack("!H", self.sendCount + 1)
        checksum = struct.pack("!H", self.generateChecksum(type + code + identifier + seqno + timestamp))
        message = type + code + checksum + identifier + seqno + timestamp
        return message
    
    # calculate checksum
    def generateChecksum(self, data):
        if len(data) % 2 != 0:
            data += b'\x00'
        res = 0
        for i in range(0, len(data), 2):
            res = self.onesComplementSum(res, (data[i] << 8) + data[i+1])
        return ~res & 0xffff
    
    # one's complement sum
    def onesComplementSum(sele, num1, num2):
        res = num1 + num2
        return res if res < 65536 else res + 1 - 65536
    
    # print statistics
    def printStats(self):
        print()
        print("--- {} ping statistics ---".format(self.serverAddress[0]))
        print("{0} transmitted, {1} received, {2}% loss, time {3} ms".format(self.sendCount, self.recvCount, (100 - self.recvCount*100//self.sendCount), int(time.time() * 1000) - self.starttime))
        try: # check empty value
            print("rtt min/avg/max = {}/{}/{}".format(min(self.rtts),sum(self.rtts)//len(self.rtts),max(self.rtts)))
        except ValueError:
            print("rtt min/avg/max = 0/0/0")


def main():
    try:
        server_ip = sys.argv[1].split('=')[1]
        server_port = int(sys.argv[2].split('=')[1])
        count = int(sys.argv[3].split('=')[1])
        period = int(sys.argv[4].split('=')[1])
        timeout = int(sys.argv[5].split('=')[1])
    except:
        print("Invalid Value!")
        return

    client = PingClient(server_ip, server_port, count, period, timeout)
    client.main()

if __name__ == "__main__":
    main()