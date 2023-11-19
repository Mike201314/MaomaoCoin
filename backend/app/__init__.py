import socket

import requests
from flask import Flask, request, abort, send_from_directory, render_template, jsonify

app = Flask(__name__)

# the address of the node
# if it is empty, this node will run as a root node
PEER_NODES = {"http://10.2.0.2:5000/"}  # a set
PORT = 5000


def broadcast_block(data):
    global PEER_NODES

    clear_dead_nodes()
    for peer in PEER_NODES:
        try:
            response = requests.post(peer + "/block", json=data)
        except requests.exceptions.ConnectionError:
            continue
        if response.status_code == 201:
            print(response.json())


def broadcast_transaction(data):
    global PEER_NODES

    clear_dead_nodes()
    for peer in PEER_NODES:
        try:
            response = requests.post(peer + "/transaction", json=data)
        except requests.exceptions.ConnectionError:
            continue
        if response.status_code == 201:
            print(response.json())


# ping all the peers to check if they are alive
def clear_dead_nodes():
    global PEER_NODES  # use the global variable

    temp_set = set()
    for peer in PEER_NODES:
        try:
            response = requests.get(peer + "/ping")
        except requests.exceptions.ConnectionError:
            temp_set.add(peer)
            continue
        if response.status_code != 200:
            temp_set.add(peer)
    PEER_NODES.difference_update(temp_set)


def get_peers():
    global PEER_NODES

    temp_set = set()
    for peer in PEER_NODES:
        try:
            response = requests.get(peer + "/nodes")
        except requests.exceptions.ConnectionError:
            continue
        if response.status_code == 200:
            print(response.json())
            temp_set.update(response.json())
    PEER_NODES.update(temp_set)


def register_self():
    global PEER_NODES

    for peer in PEER_NODES:
        try:
            response = requests.post(peer + "/register", json=[HOST_URL])
        except requests.exceptions.ConnectionError:
            continue
        if response.status_code == 201:
            print(response.json())


# query peers from the network
def update_peers():
    global PEER_NODES

    clear_dead_nodes()
    get_peers()


def get_host_ip():
    try:
        # 创建一个套接字
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 尝试连接到一个不存在的地址
        s.connect(("10.255.255.255", 1))
        # 获取本地套接字的 IP 地址
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


"""
API for interacting with other nodes

- GET /ping: ping a node to check if it is alive
- GET /nodes: get all nodes address in the network
- POST /register: add a new node to the network
- GET /block/<block_index>: get a block by its index, (-1 means the latest block)
- POST /block: create a new block
- POST /transaction: create a new transaction

"""


@app.route("/ping", methods=["GET"])
def ping():
    return "pong"


@app.route("/nodes", methods=["GET"])
def get_nodes():
    global PEER_NODES

    nodes_list = list(PEER_NODES) + [request.host_url]
    return jsonify(nodes_list)


@app.route("/register", methods=["POST"])
def register_node():
    global PEER_NODES

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    for node in data:
        PEER_NODES.add(node)
    return jsonify({"message": "New nodes have been added", "total_nodes": list(PEER_NODES)}), 201


@app.route("/block/<block_index>", methods=["GET"])
def get_block(block_index):
    return "block"


@app.route("/block", methods=["POST"])
def post_block():
    return jsonify("block"),  201


@app.route("/transaction", methods=["POST"])
def post_transaction():
    return jsonify("transaction"), 201


"""
API for interacting with the user
only accept request from the localhost

- POST /transaction: create a new transaction
- GET /unspentoutput: get all unspent outputs
- GET /mine: mine a new block
- GET /newwallet: get a new wallet
- POST /loadwallet: load a wallet 

- GET /: serve the React GUI
- GET /static/js/<path:filename>: serve the React GUI
- GET /static/css/<path:filename>: serve the React GUI
- GET /static/media/<path:filename>: serve the React GUI
- GET /<path:filename>: serve the React GUI
"""


@app.route("/transaction", methods=["POST"])
def create_transaction():
    if request.remote_addr != "127.0.0.1":
        abort(403)
    return "transaction"


@app.route("/unspentoutput", methods=["GET"])
def get_unspent_output():
    if request.remote_addr != "127.0.0.1":
        abort(403)
    return "unspentoutput"


@app.route("/mine", methods=["GET"])
def mine():
    if request.remote_addr != "127.0.0.1":
        abort(403)
    return "mine"


@app.route("/newwallet", methods=["GET"])
def new_wallet():
    if request.remote_addr != "127.0.0.1":
        abort(403)
    return "newwallet"


@app.route("/loadwallet", methods=["POST"])
def load_wallet():
    if request.remote_addr != "127.0.0.1":
        abort(403)
    return "loadwallet"


# serve the files for our React GUI
@app.route("/", methods=["GET"])
def index():
    if request.remote_addr != "127.0.0.1":
        abort(403)
    return send_from_directory("../../frontend/build", "index.html")


@app.route("/<path:filename>", methods=["GET"])
def index_default(filename):
    if request.remote_addr != "127.0.0.1":
        abort(403)
    return send_from_directory("../../frontend/build", filename)


@app.route("/static/js/<path:filename>", methods=["GET"])
def index_js(filename):
    if request.remote_addr != "127.0.0.1":
        abort(403)
    return send_from_directory("../../frontend/build/static/js", filename)


@app.route("/static/css/<path:filename>", methods=["GET"])
def index_css(filename):
    if request.remote_addr != "127.0.0.1":
        abort(403)
    return send_from_directory("../../frontend/build/static/css", filename)


@app.route("/static/media/<path:filename>", methods=["GET"])
def index_media(filename):
    if request.remote_addr != "127.0.0.1":
        abort(403)
    return send_from_directory("../../frontend/build/static/media", filename)


"""
Error handlers: customize the error page for the server
"""


@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403


# start the server
if __name__ == "__main__":
    HOST_URL = "http://" + get_host_ip() + ":" + str(PORT)
    update_peers()
    register_self()
    app.run(host="0.0.0.0", port=PORT)
