from datetime import datetime
import random
from socket import AF_INET, SOCK_DGRAM, socket
import time

from constants import *

BUFFER_SIZE = 1024
FORMAT = "utf-8"

REQUEST_HANDLED = "REQ_HANDLED"
REQUEST_REDIRECTED = "REQ_REDIRECTED"

class Client:
    def __init__(self) -> None:
        self.__socket = socket(AF_INET, SOCK_DGRAM)


    def __log(self, msg) -> None:
        print("[CLIENT] {} - {}".format(
            datetime.now().strftime("%y/%m/%d %H:%M:%S.%f"), msg))

    
    def __wait_timeout(self, start_time) -> bool:
        return time.time() - start_time >= 5 # Wait 5 seconds


    def __send_request_to(self, request:str, host, port) -> None:
        self.__socket.sendto(request.encode(FORMAT), (host, port))


    def __receive_ack(self) -> str:
        raw_ack, addr = self.__socket.recvfrom(BUFFER_SIZE)
        ack = raw_ack.decode(FORMAT)
        return ack, addr


    def start(self) -> None:
        pass
        

    def run(self) -> None:
        while True:
            request = input("[CLIENT] {} - Enter request: ".format(datetime.now().strftime("%y/%m/%d %H:%M:%S.%f")))
            request = " ".join([str(random.choice(range(0, 10000))), request])

            # Select a random server port
            RANDOM_SERVER_PORT = random.choice(
                range(LOWER_PORT_LIMIT, UPPER_PORT_LIMIT+STEP, STEP))

            # Send REQ
            self.__send_request_to(request, SERVER_HOST, RANDOM_SERVER_PORT)
            self.__log("REQ -{}- send to {}:{}".format(
                request, SERVER_HOST, RANDOM_SERVER_PORT))

            # Wait until receiving ACK
            start_time = time.time()
            while not self.__wait_timeout(start_time):
                ack, addr = self.__receive_ack()
                self.__log("ACK -{}- received from {}:{}".format(
                    ack, addr[0], addr[1]))
                
                # If ACK is REQ_HANDLED or REQ_ABORT, break
                if ack != REQUEST_REDIRECTED:
                    break


if __name__ == "__main__":
    client = Client()
    client.start()
    client.run()
