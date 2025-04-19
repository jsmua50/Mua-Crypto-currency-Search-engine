# MUA Coin Full App with Enhanced Layout Design and Login Screen
import os
import json
import hashlib
import uuid
import time
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import traceback
import requests
import threading

# Wallet Logic
WALLET_FILE = "wallet.json"
BLOCKCHAIN_FILE = "blockchain.json"
WALLET_SYNC_URL = "https://example.com/api/sync_wallet"
REWARD = 50
PRICE_API_URL = "https://example.com/api/mua_price"

# Dummy user database
USERS_FILE = "users.json"

def save_user(email, password):
    users = {} if not os.path.exists(USERS_FILE) else json.load(open(USERS_FILE))
    users[email] = hashlib.sha256(password.encode()).hexdigest()
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def authenticate_user(email, password):
    if not os.path.exists(USERS_FILE): return False
    users = json.load(open(USERS_FILE))
    return email in users and users[email] == hashlib.sha256(password.encode()).hexdigest()

def generate_wallet():
    if os.path.exists(WALLET_FILE):
        with open(WALLET_FILE, 'r') as f:
            return json.load(f)
    private_key = str(uuid.uuid4())
    public_key = hashlib.sha256(private_key.encode()).hexdigest()
    wallet = {
        "private_key": private_key,
        "public_key": public_key,
        "address": public_key[:16]
    }
    with open(WALLET_FILE, 'w') as f:
        json.dump(wallet, f)
    sync_wallet_online(wallet)
    return wallet

def get_wallet():
    return generate_wallet() if not os.path.exists(WALLET_FILE) else json.load(open(WALLET_FILE))

def sync_wallet_online(wallet):
    try:
        requests.post(WALLET_SYNC_URL, json=wallet, timeout=5)
    except:
        pass

def create_genesis_block():
    return {
        "index": 0,
        "timestamp": time.time(),
        "transactions": ["Genesis Block"],
        "previous_hash": "0",
        "hash": "genesis_hash"
    }

def load_blockchain():
    if not os.path.exists(BLOCKCHAIN_FILE):
        genesis = [create_genesis_block()]
        save_blockchain(genesis)
        return genesis
    return json.load(open(BLOCKCHAIN_FILE))

def save_blockchain(chain):
    json.dump(chain, open(BLOCKCHAIN_FILE, 'w'), indent=2)

def calculate_hash(index, timestamp, transactions, previous_hash):
    return hashlib.sha256(f"{index}{timestamp}{transactions}{previous_hash}".encode()).hexdigest()

def mine_block(wallet_address):
    chain = load_blockchain()
    last_block = chain[-1]
    index = len(chain)
    timestamp = time.time()
    transactions = [f"Mining reward -> {wallet_address}: {REWARD} MUA"]
    new_block = {
        "index": index,
        "timestamp": timestamp,
        "transactions": transactions,
        "previous_hash": last_block['hash'],
        "hash": calculate_hash(index, timestamp, transactions, last_block['hash'])
    }
    chain.append(new_block)
    save_blockchain(chain)
    return new_block

def calculate_balance(wallet_address):
    balance = 0
    for block in load_blockchain():
        for tx in block.get("transactions", []):
            if f"{wallet_address}:" in tx:
                parts = tx.split(":")
                if len(parts) == 2:
                    try:
                        balance += float(parts[1].replace("MUA", "").strip())
                    except:
                        pass
    return balance

class LoginScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login to MUA Coin")
        self.geometry("400x300")
        self.configure(bg="white")

        tk.Label(self, text="Email:", bg="white", font=("Arial", 12)).pack(pady=5)
        self.email_entry = tk.Entry(self, font=("Arial", 12))
        self.email_entry.pack(pady=5)

        tk.Label(self, text="Password:", bg="white", font=("Arial", 12)).pack(pady=5)
        self.password_entry = tk.Entry(self, show="*", font=("Arial", 12))
        self.password_entry.pack(pady=5)

        tk.Button(self, text="Login", font=("Arial", 12), command=self.login).pack(pady=10)
        tk.Button(self, text="Sign Up", font=("Arial", 12), command=self.sign_up).pack()

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        if authenticate_user(email, password):
            self.destroy()
            MUACoinApp().mainloop()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def sign_up(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        if email and password:
            save_user(email, password)
            messagebox.showinfo("Success", "Account created. You can now log in.")
        else:
            messagebox.showwarning("Warning", "Please fill out both fields.")

class MUACoinApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MUA Coin")
        self.geometry("1000x700")
        self.dark_mode = False
        self.wallet = get_wallet()
        load_blockchain()

        self.canvas = tk.Canvas(self, width=1000, height=700, highlightthickness=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.gradient_bg(self.canvas, "#7f00ff", "#00bfff")
        self.canvas.lower("all")

        self.build_ui()

        for widget in self.winfo_children():
            if widget != self.canvas:
                widget.lift()

    def build_ui(self):
        header = tk.Frame(self, bg="white")
        header.pack(side=tk.TOP, fill=tk.X)
        tk.Label(header, text="MUA Coins - Made by jsmua50", font=("Arial", 22, "bold"), bg="white").pack(side=tk.LEFT, padx=20)
        tk.Label(header, text=f"{datetime.datetime.now().strftime('%d.%m.%Y')}", font=("Arial", 16), bg="white").pack(side=tk.RIGHT, padx=20)

        tk.Frame(self, height=4, bg="black").pack(fill=tk.X)

        info_frame = tk.Frame(self, bg="white")
        info_frame.pack(fill=tk.X, pady=5)
        tk.Label(info_frame, text=f"Wallet Address: {self.wallet['address']}", font=("Arial", 14), bg="white").pack(side=tk.LEFT, padx=20)
        self.price_label = tk.Label(info_frame, text="💱 MUA Price: Loading...", font=("Arial", 14), bg="white")
        self.price_label.pack(side=tk.RIGHT, padx=20)

        main_frame = tk.Frame(self, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_panel = tk.Frame(main_frame, width=300, bg="white")
        left_panel.pack(side=tk.LEFT, fill=tk.Y)

        self.balance_label = tk.Label(left_panel, text=f"💰 Balance: {calculate_balance(self.wallet['address'])} MUA", font=("Arial", 18), bg="white")
        self.balance_label.pack(pady=20)

        mine_btn = tk.Button(left_panel, text="⛏️ Mine Block", command=self.mine_block)
        self.style_button(mine_btn)
        mine_btn.pack(pady=10)

        refresh_btn = tk.Button(left_panel, text="🔄 Refresh Balance", command=self.refresh_balance)
        self.style_button(refresh_btn)
        refresh_btn.pack(pady=10)

        center_panel = tk.Frame(main_frame, bg="white")
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(center_panel, text="🏆 Leaderboard", font=("Arial", 18), bg="white").pack(pady=10)
        for i in range(1, 6):
            tk.Label(center_panel, text=f"{i}. user{i} - 0 MUA", font=("Arial", 14), bg="white").pack()

        tk.Frame(self, height=2, bg="black").pack(fill=tk.X, pady=10)

        search_frame = tk.Frame(self, bg="white")
        search_frame.pack(pady=30)
        search_entry = tk.Entry(search_frame, font=("Arial", 14), width=50)
        search_entry.pack(side=tk.LEFT, padx=10)
        search_btn = tk.Button(search_frame, text="🔍 Search", font=("Arial", 14), command=lambda: self.search_duckduckgo(search_entry.get()))
        self.style_button(search_btn)
        search_btn.pack(side=tk.LEFT, padx=10)

        tk.Frame(self, height=2, bg="black").pack(fill=tk.X, pady=10)

        settings_frame = tk.Frame(self, bg="white")
        settings_frame.pack(fill=tk.BOTH, expand=False, pady=20)
        tk.Label(settings_frame, text="⚙️ Settings", font=("Arial", 18), bg="white").pack(pady=10)

        mode_var = tk.BooleanVar(value=self.dark_mode)
        tk.Checkbutton(settings_frame, text="Enable Dark Mode", font=("Arial", 14), variable=mode_var, bg="white",
                       command=lambda: self.toggle_dark_mode(mode_var.get())).pack()

        self.fetch_live_price()

    def gradient_bg(self, canvas, color1, color2):
        width, height = 1000, 700
        r1, g1, b1 = self.winfo_rgb(color1)
        r2, g2, b2 = self.winfo_rgb(color2)
        for i in range(height):
            nr = int(r1 + (r2 - r1) * i / height) >> 8
            ng = int(g1 + (g2 - g1) * i / height) >> 8
            nb = int(b1 + (b2 - b1) * i / height) >> 8
            canvas.create_line(0, i, width, i, fill=f"#{nr:02x}{ng:02x}{nb:02x}")

    def style_button(self, button):
        def on_enter(e): button.config(font=("Arial", 14, "bold"), relief="raised", bd=3)
        def on_leave(e): button.config(font=("Arial", 14), relief="flat", bd=1)
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        button.config(relief="flat", bd=1)

    def toggle_dark_mode(self, enable):
        self.dark_mode = enable
        bg = "gray20" if enable else "white"
        fg = "white" if enable else "black"
        def apply_theme(widget):
            try: widget.configure(bg=bg, fg=fg)
            except: pass
            for child in widget.winfo_children():
                apply_theme(child)
        apply_theme(self)

    def search_duckduckgo(self, query):
        if query:
            webbrowser.open(f"https://duckduckgo.com/?q={query}")

    def mine_block(self):
        new_block = mine_block(self.wallet['address'])
        messagebox.showinfo("Block Mined", f"Block #{new_block['index']} mined successfully!")
        self.refresh_balance()

    def refresh_balance(self):
        self.balance_label.config(text=f"💰 Balance: {calculate_balance(self.wallet['address'])} MUA")

    def fetch_live_price(self):
        def fetch():
            while True:
                try:
                    response = requests.get(PRICE_API_URL, timeout=5)
                    if response.status_code == 200:
                        price = response.json().get("price", 0)
                        self.price_label.config(text=f"💱 MUA Price: ${price:.4f}")
                except:
                    self.price_label.config(text="💱 MUA Price: N/A")
                time.sleep(30)
        threading.Thread(target=fetch, daemon=True).start()

if __name__ == "__main__":
    try:
        LoginScreen().mainloop()
    except Exception as e:
        with open("error_log.txt", "w") as f:
            f.write(traceback.format_exc())
        print("An error occurred. See error_log.txt.")
        input("Press Enter to close...")