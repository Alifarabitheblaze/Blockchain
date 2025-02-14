import time
import tkinter as tk
from tkinter import ttk


# Manual hash function
def manual_hash(data):
    hash_value = 0
    prime = 31  # Кіші жай сан
    for char in data:
        hash_value = (hash_value * prime + ord(char)) % (2 ** 16)  # Оны 16 биттік ауқымда сақтау
    return hex(hash_value)[2:]  # Оналтылық жолды қайтару


# Блок класы
class Block:
    def __init__(self, dummy_data, previous_hash="0"):
        self.timestamp = time.time()
        self.dummy_data = dummy_data
        self.previous_hash = previous_hash
        self.address = self.calculate_hash()  # Бірегей блок хэші

    def calculate_hash(self):
        block_data = f"{self.timestamp}{self.dummy_data}{self.previous_hash}"
        return manual_hash(block_data)


# Блокчейн класы
class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(dummy_data="Genesis Block")

    def add_block(self, dummy_data):
        previous_block = self.chain[-1]  # Соңғы блокты алу
        new_block = Block(dummy_data, previous_block.address)  # Жаңа блокты байланыстыру
        self.chain.append(new_block)

    def validate_chain(self):
        for i in range(1, len(self.chain)):  # Genesis блогын өткізіп жіберу
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.previous_hash != previous_block.address:
                return False  # Тізбек жарамсыз
            if current_block.address != current_block.calculate_hash():
                return False  # Хэш жарамсыз
        return True  # Тізбек жарамды

    def display_chain(self):
        for block in self.chain:
            print(f"Block Address: {block.address}")
            print(f"Timestamp: {block.timestamp}")
            print(f"Dummy Data: {block.dummy_data}")
            print(f"Previous Hash: {block.previous_hash}")
            print("-" * 40)


# Blockchain Explorer графикалық интерфейсі
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


# Мысал
blockchain = Blockchain()
blockchain.add_block("Block 1 Data")
blockchain.add_block("Block 2 Data")
blockchain.add_block("Block 3 Data")

# Консольде блокчейнді көру
blockchain.display_chain()
print("Is blockchain valid?", blockchain.validate_chain())

# GUI іске қосу
explorer = BlockchainExplorer(blockchain)
explorer.mainloop()