import socket

HOST = "0.0.0.0"
PORT = 9000

db = {}  # in-memory key-value store

def parse_resp(data):
    """
    Very basic RESP parser for arrays and bulk strings.
    Supports simple commands like PING, SET, GET.
    """
    parts = data.split(b"\r\n")
    items = []
    i = 0
    while i < len(parts):
        if parts[i].startswith(b"$"):  # bulk string for more refrence please redis serialization protocol : https://redis.io/docs/latest/develop/reference/protocol-spec/
            items.append(parts[i + 1].decode())
            i += 2
        else:
            i += 1
    return items

# Start TCP server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT)) # bind to address
    server.listen() # listen for connections
    print(f"[+] Custom Redis listening on port {PORT}")

    conn, addr = server.accept()
    print(f"[+] Connected by {addr}")

    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print("RAW DATA:", data) # Print raw received data

            try:
                cmd = parse_resp(data) # Parse RESP command
            except Exception as e:
                conn.sendall(b"-ERR invalid command\r\n")
                continue

            if not cmd:
                conn.sendall(b"-ERR empty command\r\n")
                continue

            command = cmd[0].upper()
            print("COMMAND:", command, "ARGS:", cmd[1:])

            #multiple switch case for different commands
            if command == "PING":
                conn.sendall(b"+PONG\r\n")

            elif command == "SET" and len(cmd) == 3:
                key, value = cmd[1], cmd[2]
                db[key] = value
                conn.sendall(b"+OK\r\n")

            elif command == "GET" and len(cmd) == 2:
                key = cmd[1]
                if key in db:
                    val = db[key]
                    val_bytes = val.encode()
                    conn.sendall(b"$" + str(len(val_bytes)).encode() + b"\r\n" + val_bytes + b"\r\n")
                else:
                    conn.sendall(b"$-1\r\n")  # null bulk string

            else:
                conn.sendall(b"-ERR unknown command\r\n")
