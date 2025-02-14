import time
import tkinter as tk
from tkinter import ttk
import threading
import json
import socket


def manual_hash(data):
    hash_value = 0
    prime = 31  # A small prime number
    for char in data:
        hash_value = (hash_value * prime + ord(char)) % (2 ** 16)  # Keeping it within 16-bit range
    return hex(hash_value)[2:]  # Return hexadecimal string


# Block class
class Block:
    def __init__(self, dummy_data, previous_hash="0"):
        self.timestamp = time.time()
        self.dummy_data = dummy_data
        self.previous_hash = previous_hash
        self.address = self.calculate_hash()  # Unique block hash

    def calculate_hash(self):
        block_data = f"{self.timestamp}{self.dummy_data}{self.previous_hash}"
        return manual_hash(block_data)


# Blockchain class
class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.nodes = set()

    def create_genesis_block(self):
        return Block(dummy_data="Genesis Block")

    def add_block(self, dummy_data):
        previous_block = self.chain[-1]  # Get last block
        new_block = Block(dummy_data, previous_block.address)  # Link new block
        self.chain.append(new_block)
        self.broadcast_block(new_block)

    def validate_chain(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.previous_hash != previous_block.address:
                return False
            if current_block.address != current_block.calculate_hash():
                return False
        return True

    def display_chain(self):
        for block in self.chain:
            print(f"Block Address: {block.address}")
            print(f"Timestamp: {block.timestamp}")
            print(f"Dummy Data: {block.dummy_data}")
            print(f"Previous Hash: {block.previous_hash}")
            print("-" * 40)

    def register_node(self, address):
        self.nodes.add(address)

    def broadcast_block(self, block):
        block_data = json.dumps(block.__dict__)
        for node in self.nodes:
            try:
                with socket.create_connection((node, 5000)) as sock:
                    sock.sendall(block_data.encode())
            except ConnectionRefusedError:
                pass


# Blockchain Explorer GUI
class BlockchainExplorer(tk.Tk):
    def __init__(self, blockchain):
        super().__init__()
        self.blockchain = blockchain
        self.title("Blockchain Explorer")
        self.geometry("600x400")

        tk.Label(self, text="Blockchain Explorer", font=("Arial", 16, "bold")).pack(pady=10)
        columns = ("Block Address", "Timestamp", "Dummy Data", "Previous Hash")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        self.tree.pack(expand=True, fill="both", padx=10, pady=5)

        self.status_label = tk.Label(self, text="", font=("Arial", 12))
        self.status_label.pack(pady=10)

        self.update_display()
        self.refresh_display()

    def update_display(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for block in self.blockchain.chain:
            self.tree.insert("", "end", values=(
                block.address,
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(block.timestamp)),
                block.dummy_data,
                block.previous_hash
            ))

        is_valid = self.blockchain.validate_chain()
        if is_valid:
            self.status_label.config(text="Blockchain Status: ✅ VALID", fg="green")
        else:
            self.status_label.config(text="Blockchain Status: ❌ INVALID", fg="red")

    def refresh_display(self):
        self.update_display()
        self.after(5000, self.refresh_display)


# Node Server
class NodeServer:
    def __init__(self, blockchain):
        self.blockchain = blockchain
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("0.0.0.0", 5000))
        self.server.listen(5)
        threading.Thread(target=self.listen_for_blocks, daemon=True).start()

    def listen_for_blocks(self):
        while True:
            conn, _ = self.server.accept()
            with conn:
                block_data = json.loads(conn.recv(1024).decode())
                new_block = Block(block_data['dummy_data'], block_data['previous_hash'])
                new_block.timestamp = block_data['timestamp']
                new_block.address = block_data['address']
                self.blockchain.chain.append(new_block)


# Example Usage
blockchain = Blockchain()
node_server = NodeServer(blockchain)
blockchain.register_node("localhost")
blockchain.add_block("Block 1 Data")
blockchain.add_block("Block 2 Data")
blockchain.add_block("Block 3 Data")

blockchain.display_chain()
print("Is blockchain valid?", blockchain.validate_chain())

explorer = BlockchainExplorer(blockchain)
explorer.mainloop()