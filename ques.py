import socket

HOST = "0.0.0.0"
PORT = 9000

db = {}  # in-memory key-value store: can store strings or lists
list1=[]

def parse_resp(data):
    """
    Very basic RESP parser for arrays and bulk strings.
    Supports simple commands like PING, SET, GET, LPUSH, RPUSH, LPOP, RPOP, LRANGE.
    """
    parts = data.split(b"\r\n")
    items = []
    i = 0
    while i < len(parts):
        if parts[i].startswith(b"$"):  # bulk string
            items.append(parts[i + 1].decode())
            i += 2
        else:
            i += 1
    return items

def encode_simple_string(s):
    return f"+{s}\r\n".encode()

def encode_bulk_string(s):
    return f"${len(s)}\r\n{s}\r\n".encode()

def encode_array(arr):
    resp = f"*{len(arr)}\r\n"
    for item in arr:
        resp += f"${len(item)}\r\n{item}\r\n"
    return resp.encode()

def encode_integer(n):
    return f":{n}\r\n".encode()

# Start TCP server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen()
    print(f"[+] Custom Redis listening on port {PORT}")

    conn, addr = server.accept()
    print(f"[+] Connected by {addr}")

    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print("RAW DATA:", data)

            try:
                cmd = parse_resp(data)
            except Exception:
                conn.sendall(b"-ERR invalid command\r\n")
                continue

            if not cmd:
                conn.sendall(b"-ERR empty command\r\n")
                continue

            command = cmd[0].upper()  # First element is the command
            args = cmd[1:]
            print("COMMAND:", command, "ARGS:", args)

            if command == "PING":
                conn.sendall(encode_simple_string("PONG"))

            elif command == "SET" and len(args) == 2:
                key, value = args
                print("SETTING:", key, "TO:", value)
                db[key] = value
                conn.sendall(encode_simple_string("OK"))

            elif command == "GET" and len(args) == 1:
                key = args[0]
                print("GETTING:", key)
                value = db.get(key)
                if value is None:
                    conn.sendall(encode_bulk_string(""))  # Nil
                else:
                    conn.sendall(encode_bulk_string(value))

            elif command == "LPUSH" and len(args) == 2:
                key, value = args
                print("LPUSH:", key, "VALUE:", value)
                lst = db.setdefault(key, [])
                print("CURRENT LIST:", lst)
                if not isinstance(lst, list):
                    conn.sendall(b"-ERR wrong type\r\n")
                    continue
                lst.insert(0, value)
                print("UPDATED LIST:", lst)
                conn.sendall(encode_integer(len(lst)))

            elif command == "RPUSH" and len(args) == 2:
                key, value = args
                print("RPUSH:", key, "VALUE:", value)
                lst = db.setdefault(key, [])
                print("CURRENT LIST:", lst)
                if not isinstance(lst, list):
                    conn.sendall(b"-ERR wrong type\r\n")
                    continue
                lst.append(value)
                print("UPDATED LIST:", lst)
                conn.sendall(encode_integer(len(lst)))

            elif command == "LPOP" and len(args) == 1:
                key = args[0]
                lst = db.get(key)
                print("LPOP FROM LIST:", lst)
                if not lst:
                    conn.sendall(encode_bulk_string(""))  # Empty / nil
                elif not isinstance(lst, list):
                    conn.sendall(b"-ERR wrong type\r\n")
                else:
                    value = lst.pop(0)
                    conn.sendall(encode_bulk_string(value))

            elif command == "RPOP" and len(args) == 1:
                key = args[0]
                lst = db.get(key)
                print("RPOP FROM LIST:", lst)
                if not lst:
                    conn.sendall(encode_bulk_string(""))  # Empty / nil
                elif not isinstance(lst, list):
                    conn.sendall(b"-ERR wrong type\r\n")
                else:
                    value = lst.pop()
                    conn.sendall(encode_bulk_string(value))

            elif command == "LRANGE" and len(args) == 3:
                key, start, end = args
                print("LRANGE ARGS:", key, start, end)
                lst = db.get(key)
                if not isinstance(lst, list):
                    conn.sendall(b"-ERR wrong type or no such key\r\n")
                    continue
                start, end = int(start), int(end)
                slice_lst = lst[start:end + 1] if end != -1 else lst[start:]
                conn.sendall(encode_array(slice_lst))

            else:
                conn.sendall(b"-ERR unknown or wrong number of args\r\n")
