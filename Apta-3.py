from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import base64
import tkinter as tk
from tkinter import messagebox


# Generate a new RSA key pair
def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem, public_pem


# Encrypt data with a public key
def encrypt_message(public_key, message):
    public_key = serialization.load_pem_public_key(public_key)
    encrypted = public_key.encrypt(
        message.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return base64.b64encode(encrypted).decode()


# Decrypt data with a private key
def decrypt_message(private_key, encrypted_message):
    private_key = serialization.load_pem_private_key(private_key, password=None)
    decrypted = private_key.decrypt(
        base64.b64decode(encrypted_message),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted.decode()


# Sign a message with a private key
def sign_message(private_key, message):
    private_key = serialization.load_pem_private_key(private_key, password=None)
    signature = private_key.sign(
        message.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode()


# Verify a signature with a public key
def verify_signature(public_key, message, signature):
    public_key = serialization.load_pem_public_key(public_key)
    try:
        public_key.verify(
            base64.b64decode(signature),
            message.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except:
        return False


# Tkinter Wallet GUI
class WalletApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Blockchain Wallet")
        self.private_key, self.public_key = generate_key_pair()

        self.balance_label = tk.Label(root, text="Balance: 0 BTC")
        self.balance_label.pack()

        self.sign_btn = tk.Button(root, text="Sign Message", command=self.sign_transaction)
        self.sign_btn.pack()

        self.verify_btn = tk.Button(root, text="Verify Signature", command=self.verify_transaction)
        self.verify_btn.pack()

    def sign_transaction(self):
        message = "Transaction Data"
        signature = sign_message(self.private_key, message)
        messagebox.showinfo("Signature", signature)

    def verify_transaction(self):
        message = "Transaction Data"
        signature = sign_message(self.private_key, message)
        valid = verify_signature(self.public_key, message, signature)
        messagebox.showinfo("Verification", "Valid Signature" if valid else "Invalid Signature")


if __name__ == "__main__":
    root = tk.Tk()
    app = WalletApp(root)
    root.mainloop()