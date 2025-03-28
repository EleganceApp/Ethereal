# EtherealAccount.pyw - User Account Management System
import tkinter as tk
from tkinter import ttk, messagebox, font
import os
import json
import hashlib
import subprocess
import sys
import traceback
from datetime import datetime, timedelta

# Constants
ACCOUNT_FOLDER = "Account"
LICENSE_FOLDER = "License"
os.makedirs(ACCOUNT_FOLDER, exist_ok=True)
os.makedirs(LICENSE_FOLDER, exist_ok=True)

ACCOUNTS_FILE = os.path.join(ACCOUNT_FOLDER, "accounts.json")
LICENSE_FILE = os.path.join(LICENSE_FOLDER, "keys.json")

class AccountManager:
    @staticmethod
    def load_accounts():
        """Load existing accounts from JSON file"""
        try:
            if os.path.exists(ACCOUNTS_FILE):
                with open(ACCOUNTS_FILE, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load accounts: {str(e)}")
            return {}

    @staticmethod
    def save_accounts(accounts):
        """Save accounts to JSON file"""
        try:
            with open(ACCOUNTS_FILE, 'w') as f:
                json.dump(accounts, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save accounts: {str(e)}")

    @staticmethod
    def hash_password(password):
        """Securely hash passwords"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def load_licenses():
        """Load existing licenses from JSON file"""
        try:
            if os.path.exists(LICENSE_FILE):
                with open(LICENSE_FILE, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load licenses: {str(e)}")
            return {}

    @staticmethod
    def save_licenses(licenses):
        """Save licenses to JSON file"""
        try:
            with open(LICENSE_FILE, 'w') as f:
                json.dump(licenses, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save licenses: {str(e)}")

    @staticmethod
    def validate_license(username):
        """Check if license is valid"""
        licenses = AccountManager.load_licenses()
        if username in licenses:
            license_data = licenses[username]
            if 'expiry' in license_data:
                try:
                    expiry_date = datetime.strptime(license_data['expiry'], "%Y-%m-%d")
                    return expiry_date > datetime.now()
                except:
                    return False
            return True
        return False

class EtherealAccountApp:
    def __init__(self, root):
        self.root = root
        self.accounts = AccountManager.load_accounts()  # Load existing accounts
        self.current_user = None
        self.setup_ui()

    def setup_ui(self):
        """Initialize the main application window"""
        self.root.title("Ethereal Account Manager")
        self.root.geometry("600x400")
        self.root.configure(bg="#0f1923")
        self.root.resizable(False, False)

        # Make sure window appears in foreground
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)

        self.show_login_screen()

    def show_login_screen(self):
        """Display the login screen"""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Custom fonts
        title_font = font.Font(family="Arial", size=24, weight="bold")
        header_font = font.Font(family="Segoe UI", size=16)
        button_font = font.Font(family="Segoe UI", size=12, weight="bold")

        # Main container
        main_frame = tk.Frame(self.root, bg="#0f1923")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)

        # Header
        tk.Label(main_frame, text="ETHEREAL ACCOUNTS", 
                fg="#00f2ff", bg="#0f1923", font=title_font).pack(pady=(0, 20))

        # Login Frame
        login_frame = tk.Frame(main_frame, bg="#0f1923")
        login_frame.pack(fill=tk.X)

        tk.Label(login_frame, text="Username:", 
               fg="white", bg="#0f1923", font=header_font).grid(row=0, column=0, sticky="w", pady=5)
        self.username_entry = ttk.Entry(login_frame, width=25, font=header_font)
        self.username_entry.grid(row=0, column=1, padx=10)

        tk.Label(login_frame, text="Password:", 
               fg="white", bg="#0f1923", font=header_font).grid(row=1, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(login_frame, width=25, show="•", font=header_font)
        self.password_entry.grid(row=1, column=1, padx=10)

        # Buttons
        btn_frame = tk.Frame(main_frame, bg="#0f1923")
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Login", bg="#00f2ff", fg="#0f1923",
                 font=button_font, padx=20, command=self.login).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Register", bg="#2a2e35", fg="white",
                 font=button_font, padx=15, command=self.show_register).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Exit", bg="#d33f49", fg="white",
                 font=button_font, padx=20, command=self.root.quit).pack(side=tk.RIGHT, padx=10)

        # Status bar
        self.status_var = tk.StringVar()
        tk.Label(main_frame, textvariable=self.status_var, 
                fg="#00f2ff", bg="#0f1923", font=font.Font(size=10)).pack(side=tk.BOTTOM)

    def show_register(self):
        """Show registration dialog"""
        register_dialog = tk.Toplevel(self.root)
        register_dialog.title("Register New Account")
        register_dialog.geometry("400x350")
        register_dialog.resizable(False, False)
        register_dialog.configure(bg="#0f1923")
        register_dialog.grab_set()

        # Registration form
        tk.Label(register_dialog, text="Create New Account", 
               fg="#00f2ff", bg="#0f1923", font=("Arial", 16)).pack(pady=10)

        fields = ["Username:", "Password:", "Confirm Password:", "Email:", "License Key (optional):"]
        reg_entries = {}
        
        for i, field in enumerate(fields):
            tk.Label(register_dialog, text=field, 
                   fg="white", bg="#0f1923").pack(pady=(5,0))
            entry = ttk.Entry(register_dialog, width=30)
            if "Password" in field:
                entry.config(show="•")
            entry.pack()
            reg_entries[field.replace(":", "").lower().replace(" ", "_")] = entry

        def register():
            """Handle account registration"""
            username = reg_entries['username'].get().strip()
            password = reg_entries['password'].get()
            confirm = reg_entries['confirm_password'].get()
            email = reg_entries['email'].get().strip()
            license_key = reg_entries['license_key_(optional)'].get().strip()

            # Validation checks
            if not all([username, password, confirm, email]):
                messagebox.showerror("Error", "All fields except license key are required")
                return

            if password != confirm:
                messagebox.showerror("Error", "Passwords don't match")
                return

            if username in self.accounts:
                messagebox.showerror("Error", "Username already exists")
                return

            if "@" not in email or "." not in email:
                messagebox.showerror("Error", "Invalid email address")
                return

            # Add new account to existing accounts
            self.accounts[username] = {
                'password': AccountManager.hash_password(password),
                'email': email,
                'created': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'license_key': license_key if license_key else None
            }
            
            # Save the updated accounts
            AccountManager.save_accounts(self.accounts)

            # Save license if provided
            if license_key:
                licenses = AccountManager.load_licenses()
                licenses[username] = {
                    'key': license_key,
                    'valid': True,
                    'activated': datetime.now().strftime("%Y-%m-%d"),
                    'expiry': (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
                }
                AccountManager.save_licenses(licenses)

            messagebox.showinfo("Success", "Account created successfully!")
            register_dialog.destroy()
            self.current_user = username
            self.show_profile()

        tk.Button(register_dialog, text="Register", bg="#00f2ff",
                 command=register).pack(pady=20)

    def login(self):
        """Handle user login with existing accounts"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            self.status_var.set("Please enter both username and password")
            return

        # Check against stored accounts
        if username in self.accounts:
            hashed_pw = AccountManager.hash_password(password)
            if self.accounts[username]['password'] == hashed_pw:
                self.current_user = username
                self.show_profile()
            else:
                self.status_var.set("Invalid password")
                self.password_entry.delete(0, tk.END)
        else:
            self.status_var.set("Account not found")
            self.password_entry.delete(0, tk.END)

    def show_profile(self):
        """Show user profile with account details"""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Custom fonts
        title_font = font.Font(family="Arial", size=24, weight="bold")
        header_font = font.Font(family="Segoe UI", size=14)
        text_font = font.Font(family="Segoe UI", size=12)

        # Main container
        main_frame = tk.Frame(self.root, bg="#0f1923")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)

        # Header
        tk.Label(main_frame, text=f"WELCOME BACK, {self.current_user.upper()}!", 
                fg="#00f2ff", bg="#0f1923", font=title_font).pack(pady=(0, 20))

        # Profile info frame
        info_frame = tk.Frame(main_frame, bg="#0f1923")
        info_frame.pack(fill=tk.X, pady=10)

        # Display account details from stored data
        account_data = self.accounts[self.current_user]
        tk.Label(info_frame, text=f"Email: {account_data['email']}", 
               fg="white", bg="#0f1923", font=text_font).pack(anchor="w")
        tk.Label(info_frame, text=f"Member since: {account_data['created']}", 
               fg="white", bg="#0f1923", font=text_font).pack(anchor="w")

        # License status
        license_status = AccountManager.validate_license(self.current_user)
        status_color = "#00ff00" if license_status else "#ff0000"
        status_text = "ACTIVE" if license_status else "INACTIVE"
        
        license_frame = tk.Frame(main_frame, bg="#0f1923")
        license_frame.pack(fill=tk.X, pady=20)
        
        tk.Label(license_frame, text="LICENSE STATUS:", 
               fg="white", bg="#0f1923", font=header_font).pack(side=tk.LEFT)
        tk.Label(license_frame, text=status_text, 
               fg=status_color, bg="#0f1923", font=header_font).pack(side=tk.LEFT, padx=10)

        # Buttons
        btn_frame = tk.Frame(main_frame, bg="#0f1923")
        btn_frame.pack(fill=tk.X, pady=20)

        tk.Button(btn_frame, text="Launch Application", bg="#00f2ff", fg="#0f1923",
                font=text_font, padx=20, command=self.open_main_app).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Logout", bg="#2a2e35", fg="white",
                font=text_font, padx=20, command=self.show_login_screen).pack(side=tk.RIGHT, padx=5)

    def open_main_app(self):
        """Launch the main application"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            ethereal_path = os.path.join(script_dir, "Ethereal.pyw")
            
            if not os.path.exists(ethereal_path):
                messagebox.showerror("Error", f"Main application not found at:\n{ethereal_path}")
                return
            
            # Launch without showing a console window
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            subprocess.Popen(
                [sys.executable, ethereal_path],
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch application:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = EtherealAccountApp(root)
    root.mainloop()