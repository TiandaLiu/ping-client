# Ping Client

## Ping Server setup:
There is a Ping server file in the folder called pingserver.jar 

To run the Ping server:

    java -jar pingserver.jar --port=<port>
                            [--loss_rate=<rate>]
                            [--bit_error_rate=<rate>]
                            [--avg_delay=<delay>]

For example:

    java -jar pingserver.jar --port=8080 --loss_rate=0.1 --bit_error_rate=0.2 --avg_delay=500

If the server is set up correctly, you will see:

    Ping server listening on UDP port 8080 ...

## Ping Client setup:
There is a Ping client file in the folder called pingclient.py

To run the Ping client:

    python3 pingclient.py --server_ip=<server ip addr>
                          --server_port=<server port>
                          --count=<number of pings to send>
                          --period=<wait interval>
                          --timeout=<timeout>

For example:

    python3 pingclient.py --server_ip=127.0.0.1 --server_port=8080 --count=5 --period=1000 --timeout=5000

If the client is set up correctly, you will see:

    PING 127.0.0.1
    PONG 127.0.0.1: seq=3 time=645ms
    PONG 127.0.0.1: seq=4 time=349ms
    PONG 127.0.0.1: seq=5 time=752ms

    --- 127.0.0.1 ping statistics ---
    5 transmitted, 3 received, 40% loss, time 10771 ms
    rtt min/avg/max = 349/582/752