# virtualmachine.py

import hashlib
import time
import sys
import curses

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


class Wallet:
    def __init__(self, P3Address, QSE_balance):
        self.address = P3Address
        self.balance = QSE_balance


    def view_wallet(self):
        try:
            # Initialize curses
            stdscr = curses.initscr()
            curses.start_color()
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Border color
            curses.curs_set(0)  # Hide cursor
            stdscr.clear()

            # Get terminal dimensions
            terminal_height, terminal_width = stdscr.getmaxyx()

            # Create a window for the wallet UI
            wallet_window = curses.newwin(terminal_height, terminal_width, 0, 0)

            # Define wallet data
            user_address = self.address
            qse_balance = self.balance  # Example balance, replace with actual balance
            tabs = ["Wallet", "NFTs", "Apps", "Swap"]

            # Display wallet UI
            wallet_window.addstr(1, 1, "Crypto Wallet", curses.A_BOLD)
            wallet_window.addstr(3, 1, "Address:", curses.A_BOLD)
            wallet_window.addstr(3, 12, user_address)
            wallet_window.addstr(5, 1, "QSE Balance:", curses.A_BOLD)
            wallet_window.addstr(5, 15, f"{qse_balance}")
            wallet_window.addstr(7, 1, "Tabs:", curses.A_BOLD)
            for i, tab in enumerate(tabs):
                tab_position = 9 + i * 2
                if i == 0:  # Highlight the first tab
                    wallet_window.addstr(tab_position, 1, tab, curses.A_BOLD | curses.color_pair(1))
                else:
                    wallet_window.addstr(tab_position, 1, tab)

            # Refresh the wallet window to display changes
            wallet_window.refresh()

            # Wait for user input
            wallet_window.getch()

        except KeyboardInterrupt:
            curses.endwin()  # End curses session

class VirtualMachine:
    def __init__(self, virtual_os, filesystem):  # Pass VirtualOS instance as an argument
        self.virtual_os = virtual_os  # Store reference to VirtualOS instance
        self.filesystem = filesystem

    def run(self):
        print("Running Virtual Machine...")
        # Implement VM logic here
