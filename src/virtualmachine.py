# virtualmachine.py

import hashlib
import hmac
import secrets
import base64
import time
import sys
import getpass
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

class Transaction:
    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount

class Block:
    def __init__(self, transactions, previous_hash):
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = time.time()
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        # Calculate the hash of the block
        block_content = str(self.transactions) + str(self.timestamp) + str(self.previous_hash) + str(self.nonce)
        return hashlib.sha256(block_content.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []

    def create_genesis_block(self):
        # Create the first block in the chain
        return Block(transactions=[], previous_hash="0")

    def add_block(self, new_block):
        # Add a new block to the chain
        new_block.previous_hash = self.chain[-1].hash
        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)

    def is_chain_valid(self):
        # Check if the blockchain is valid
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

    def mine_block(self):
        # Mine a new block with pending transactions
        if not self.pending_transactions:
            return False
        new_block = Block(transactions=self.pending_transactions, previous_hash=self.chain[-1].hash)
        new_block.calculate_hash()
        self.add_block(new_block)
        self.pending_transactions = []
        return True

    def add_transaction(self, transaction):
        # Add a new transaction to the pending transactions list
        self.pending_transactions.append(transaction)

    def get_balance(self, address):
        # Get the balance of a wallet address
        balance = 0
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.sender == address:
                    balance -= transaction.amount
                elif transaction.recipient == address:
                    balance += transaction.amount
        return balance


class AddressTools:
    def __init__(self):
        self.p3address = None
        self.worlist = None

    def grab_wordlist(self):
        # Load BIP39 word list
        with open("wordlist/bip39.txt", "r") as f:
            self.wordlist = [word.strip() for word in f.readlines()]
        return self.wordlist

    def generate_seed_phrase(self, wordlist):
        # Generate a random 12-word seed phrase using BIP39 word list
        seed_phrase = ' '.join(secrets.choice(wordlist) for _ in range(12))
        return seed_phrase

    def generate_crypto_address(self, fs, addrtools, seed_phrase, recover=False):
        if recover:
            print("Wallet Restore and Recovery")
        else:
            print("Setting up P3 address")
        pass1 = getpass.getpass("Enter password: ")
        pass2 = getpass.getpass("Enter password again: ")
        if addrtools.generate_hash(self, pass1) != addrtools.generate_hash(self, pass2):
            print("Passwords do not match")
            address = None
            return address
        else:
            wallet_hash = addrtools.generate_hash(self, pass1)

        #9 Derive seed bytes from seed phrase
        seed_bytes = hashlib.pbkdf2_hmac('sha512', seed_phrase.encode(), wallet_hash.encode(), 2048)

        # Use HMAC-SHA256 to generate a pseudo crypto address
        address = hmac.new(seed_bytes[:32], b'P3', hashlib.sha256).hexdigest()[:10]
        if recover:
            cryptod_hash = fs.read_file("/usr/cryptod")
            addr_file = fs.read_file("/usr/addr")
            if (f"{addrtools.generate_hash(self, seed_phrase)}:{wallet_hash}") == cryptod_hash:
                return f"P3:{address}"
        else:
            cryptod_hash = fs.create_file("/usr/cryptod", (f"{addrtools.generate_hash(self, seed_phrase)}:{wallet_hash}"))
            addr_file = fs.create_file("/usr/addr", f"P3:{address}")
            return f"P3:{address}"


    def generate_hash(self, data):
        # Use SHA-256 hashing algorithm for password encryption
        hashed_data = hashlib.sha256(data.encode()).digest()
        # Encode the hashed password using base64 for storage
        return base64.b64encode(hashed_data).decode()



class Wallet:
    def __init__(self, P3Address, QSE_balance):
        self.address = P3Address
        self.balance = QSE_balance
        self.wallet_locked = True
        self.hash_file = "/usr/cryptod"
        self.addr_file = "/usr/addr"


    def view_wallet(self, fs, addrtools):
        try:
            if self.wallet_locked:
                password = getpass.getpass("Enter password: ")
                pass_hash = addrtools.generate_hash(self, password)
                cryptod_hash = fs.read_file(self.hash_file)
                addr_cont = fs.read_file(self.addr_file)
                cryptod_pass_hash = cryptod_hash.strip().split(':')
                if cryptod_pass_hash[1] == pass_hash:
                    self.wallet_locked = False
                    self.address = addr_cont
                else:
                    print(f"Incorrect password for {addr_cont}")
            # Initialize console
            console = Console()

            # Define wallet data
            user_address = self.address
            qse_balance = self.balance  # Example balance, replace with actual balance
            tabs = ["Wallet", "NFTs", "Apps", "Swap"]

            # Create table for wallet information
            table = Table(title="Crypto Wallet")
            table.add_column("Field", justify="right", style="cyan", no_wrap=True)
            table.add_column("Value", justify="left", style="magenta")

            table.add_row("Address:", user_address)
            table.add_row("QSE Balance:", str(qse_balance))
#            table.add_row("Tabs:", ", ".join(tabs))

            # Create a panel to display the table
            panel = Panel(table, expand=False)

            # Render the panel
            console.print(panel)

            # Wait for user input
            console.input("Press Enter to continue...")
            self.wallet_locked = True

        except KeyboardInterrupt:
            console.print("\nExiting wallet view.")
            self.wallet_locked = True

class VirtualMachine:
    def __init__(self, virtual_os, filesystem):  # Pass VirtualOS instance as an argument
        self.virtual_os = virtual_os  # Store reference to VirtualOS instance
        self.filesystem = filesystem

    def run(self):
        print("Running Virtual Machine...")
        # Implement VM logic here
