import hashlib
import time
import json
import base64
import tkinter as tk
from tkinter import messagebox
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes


# Generate key pair
def generate_key_pair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key


# Hash function
def hash_data(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


# Transaction structure
class Transaction:
    def __init__(self, sender_pub_key, receiver_pub_key, amount):
        self.sender = hash_data(sender_pub_key)
        self.receiver = hash_data(receiver_pub_key)
        self.amount = amount
        self.timestamp = time.time()
        self.tx_id = self.calculate_tx_id()

    def calculate_tx_id(self):
        return hash_data(
            {"sender": self.sender, "receiver": self.receiver, "amount": self.amount, "timestamp": self.timestamp})


# Merkle Tree
class MerkleTree:
    @staticmethod
    def compute_merkle_root(transactions):
        if not transactions:
            return None
        tx_hashes = [tx.tx_id for tx in transactions]
        while len(tx_hashes) > 1:
            temp_hashes = []
            for i in range(0, len(tx_hashes), 2):
                if i + 1 < len(tx_hashes):
                    combined = tx_hashes[i] + tx_hashes[i + 1]
                else:
                    combined = tx_hashes[i]
                temp_hashes.append(hash_data(combined))
            tx_hashes = temp_hashes
        return tx_hashes[0]


# Block structure
class Block:
    def __init__(self, transactions, previous_hash):
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.merkle_root = MerkleTree.compute_merkle_root(transactions)
        self.timestamp = time.time()
        self.block_hash = self.calculate_block_hash()

    def calculate_block_hash(self):
        return hash_data(
            {"merkle_root": self.merkle_root, "previous_hash": self.previous_hash, "timestamp": self.timestamp})


# Blockchain
class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.utxo = {}

    def create_genesis_block(self):
        return Block([], "0")

    def add_block(self, transactions):
        new_block = Block(transactions, self.chain[-1].block_hash)
        if self.validate_block(new_block):
            self.chain.append(new_block)
            self.update_utxo(transactions)

    def validate_block(self, block):
        return block.merkle_root == MerkleTree.compute_merkle_root(block.transactions)

    def update_utxo(self, transactions):
        for tx in transactions:
            self.utxo[tx.receiver] = self.utxo.get(tx.receiver, 100) + tx.amount
            self.utxo[tx.sender] = self.utxo.get(tx.sender, 100) - tx.amount


# Tkinter Wallet GUI
class WalletApp:
    def __init__(self, root, blockchain):
        self.root = root
        self.root.title("Blockchain Wallet")
        self.blockchain = blockchain
        self.private_key, self.public_key = generate_key_pair()

        self.balance_label = tk.Label(root, text=f"Balance: {self.get_balance()} coins")
        self.balance_label.pack()

        self.transact_btn = tk.Button(root, text="Send Transaction", command=self.send_transaction)
        self.transact_btn.pack()

        self.explore_btn = tk.Button(root, text="Explore Blockchain", command=self.explore_blockchain)
        self.explore_btn.pack()

    def get_balance(self):
        return self.blockchain.utxo.get(hash_data(self.public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                                                               format=serialization.PublicFormat.SubjectPublicKeyInfo).decode()),
                                        100)

    def send_transaction(self):
        receiver_private_key, receiver_public_key = generate_key_pair()
        transaction = Transaction(
            self.public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                         format=serialization.PublicFormat.SubjectPublicKeyInfo).decode(),
            receiver_public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                             format=serialization.PublicFormat.SubjectPublicKeyInfo).decode(),
            10
        )
        self.blockchain.add_block([transaction])
        self.balance_label.config(text=f"Balance: {self.get_balance()} coins")
        messagebox.showinfo("Transaction", f"Transaction Sent! TxID: {transaction.tx_id}")

    def explore_blockchain(self):
        explorer_window = tk.Toplevel(self.root)
        explorer_window.title("Blockchain Explorer")

        for block in self.blockchain.chain:
            block_info = tk.Label(explorer_window,
                                  text=f"Block Hash: {block.block_hash}\nMerkle Root: {block.merkle_root}\nPrevious Hash: {block.previous_hash}\nTimestamp: {block.timestamp}\n",
                                  justify="left")
            block_info.pack()


if __name__ == "__main__":
    blockchain = Blockchain()
    root = tk.Tk()
    app = WalletApp(root, blockchain)
    root.mainloop()