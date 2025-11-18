🧠 Custom Redis Server (Python + Sockets)

This is a minimal implementation of a Redis-like server in pure Python using socket. It listens on a TCP port and supports a subset of Redis commands using the Redis Serialization Protocol (RESP).

🚀 Features

This lightweight Redis clone supports the following commands:

String Commands

PING

SET <key> <value>

GET <key>

List Commands

LPUSH <key> <value>

RPUSH <key> <value>

LPOP <key>

RPOP <key>

LRANGE <key> <start> <end>

🧰 How It Works

The server listens on TCP port 9000 (0.0.0.0:9000).

Data is stored in-memory in a Python dictionary (db).

Uses RESP to encode/decode commands.

Supports both simple strings, bulk strings, arrays, and integers as return types.

🛠 Getting Started
1. Clone the Repo (or create the file locally)
git clone <repo-url>
cd <repo-folder>

2. Run the Server
python3 redis_server.py


You should see:

[+] Custom Redis listening on port 9000

💬 Interact with the Server

You can test this using a Redis client or even telnet:

Using redis-cli
redis-cli -p 9000


Example commands:

PING
SET name Ritam
GET name
LPUSH list1 apple
LPUSH list1 banana
LRANGE list1 0 -1

Or via telnet:
telnet localhost 9000


Commands must be encoded in RESP format. Example:

*2
$4
PING

📦 Code Overview

socket is used for network communication.

parse_resp() handles Redis protocol parsing.

Commands are routed based on the input and validated including correct arguments.

🧪 Sample Output
[+] Custom Redis listening on port 9000
[+] Connected by ('127.0.0.1', 54321)
RAW DATA: b'*1\r\n$4\r\nPING\r\n'
COMMAND: PING ARGS: []
RAW DATA: b'*3\r\n$3\r\nSET\r\n$4\r\nname\r\n$5\r\nRitam\r\n'
COMMAND: SET ARGS: ['name', 'Ritam']

📝 TODO

Support more Redis commands (DEL, EXPIRE, etc.)

Implement persistence (RDB/AOF-like behavior)

Handle multiple client sessions concurrently

Add error logging and edge-case handling
