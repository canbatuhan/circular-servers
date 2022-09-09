#!/usr/bin/bash

# Greeting
echo "--------------------------------------------------------"
echo "------------------- CIRCULAR SERVERS -------------------"
echo "--------------------------------------------------------"
echo "---------------- Common Host: 127.0.0.1 ----------------"
echo "----------- Server Ports: 8010 - 8020 - 8030 -----------"
echo "--------------------------------------------------------"

# Constants
PORT=8010
STEP=10

# Start servers from port 8010 to 8030
while [ $PORT -le 8030 ]
do
    start python server.py -port=$PORT
    PORT=$(($PORT+$STEP))
done

# Start a client
start python client.py