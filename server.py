import argparse
from datetime import datetime
import random

from socket import AF_INET, SOCK_DGRAM, socket
from smpai import FiniteStateMachine

from constants import *

parser = argparse.ArgumentParser()
parser.add_argument("-port", "--port", required=True, type=int)
args = vars(parser.parse_args())
PORT = args["port"]


class Server:
    def __init__(self, host, port, config_file_path) -> None:
        self.__host = host
        self.__port = port
        self.__socket = socket(AF_INET, SOCK_DGRAM)
        self.__statemachine = FiniteStateMachine(config_file_path)
        self.__last_request_id = -1
        self.__next_server_addr = (self.__host, self.__port+STEP if self.__port < UPPER_PORT_LIMIT else LOWER_PORT_LIMIT)
        self.__prev_server_addr = (self.__host, self.__port-STEP if self.__port > LOWER_PORT_LIMIT else UPPER_PORT_LIMIT)


    def __log(self, msg) -> None:
        print("[SERVER] {} - {}".format(
            datetime.now().strftime("%y/%m/%d %H:%M:%S.%f"), msg))


    def __receive_request(self) -> str:
        raw_request, source_addr = self.__socket.recvfrom(BUFFER_SIZE)
        request = raw_request.decode(FORMAT)
        return request, source_addr


    def __extract_data(self, request_as_str:str):
        name = size = client_addr = None
        request_arr = request_as_str.split(SEPERATOR)
        request_id = request_arr.pop(0) # First element is REQ_ID
        command = request_arr.pop(0) # Second element is CMD
        name = request_arr.pop(0) # Third element is NAME

        # LOAD command format: REQ_ID LOAD VAR_NAME CLIENT_ADDR* 
        if command == "LOAD" and len(request_arr) == 1:
            client_addr = request_arr.pop(0).split(":")
            client_addr = (client_addr[0], int(client_addr[1]))

        # STORE command format: REQ_ID LOAD VAR_NAME SIZE CLIENT_ADDR*
        elif command == "STORE": 
            size = int(request_arr.pop(0))
            if len(request_arr) == 1:
                client_addr = request_arr.pop(0).split(":")
                client_addr = (client_addr[0], int(client_addr[1]))

        data = {"command": command, "name": name, "size": size}
        return request_id, data, client_addr


    def __handle(self, data:dict) -> str:
        self.__statemachine.get_context().set_variable("data", data)
        self.__statemachine.send_event(data.get("command")) # LOAD or STORE
        is_success = self.__statemachine.get_context().get_variable("is_success")

        if is_success: # If successful REQ is handled
            self.__statemachine.send_event("DONE")
            return REQUEST_HANDLED

        else: # If not successful REQ is redirected
            self.__statemachine.send_event("REDIRECT")
            return REQUEST_REDIRECTED


    def __redirect_request(self, request:str, source_addr:tuple) -> None:
        if source_addr == self.__next_server_addr: # REQ comes from NEXT, so re-direct to PREV
            self.__socket.sendto(request.encode(FORMAT), self.__prev_server_addr)

        elif source_addr == self.__prev_server_addr: # REQ comes from PREV, so re-direct to NEXT
            self.__socket.sendto(request.encode(FORMAT), self.__next_server_addr)

        else: # REQ comes from CLIENT, so re-direct randomly
            request += " {}:{}".format(source_addr[0], source_addr[1])
            neighbour_addr = random.choice([self.__next_server_addr, self.__prev_server_addr])
            self.__socket.sendto(request.encode(FORMAT), neighbour_addr)


    def __send_ack(self, raw_ack:str, addr) -> None:
        ack = raw_ack.encode(FORMAT)
        self.__socket.sendto(ack, addr)


    def start(self) -> None:
        self.__socket.bind((self.__host, self.__port))
        self.__statemachine.start()


    def run(self) -> None:
        while True:
            request, source_addr = self.__receive_request() # Receive REQ 
            request_id, data, client_addr = self.__extract_data(request) # Extract data

            if self.__last_request_id == request_id: # If it was already processed
                self.__send_ack(REQUEST_ABORT, client_addr) # REQ is aborted
                continue # Do not handle or redirect anything

            ack = self.__handle(data) # Handle request

            if ack == REQUEST_REDIRECTED: # Redirect REQ, if neccessary
                self.__redirect_request(request, source_addr)

            if client_addr is not None: # Send ACK to referenced client address
                self.__send_ack(ack, client_addr) 

            else: # Send ACK directly to the client
                self.__send_ack(ack, source_addr)
            
            self.__last_request_id = request_id # Assign the request as `last`


if __name__ == "__main__":
    server = Server(HOST, PORT, CONFIG)
    server.start()
    server.run()