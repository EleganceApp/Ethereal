# EtherealAccount.pyw - User Account Management System v1.0.0
import tkinter as tk
from tkinter import ttk, messagebox, font
import os
import json
import hashlib
import subprocess
import sys
import webbrowser
from datetime import datetime, timedelta

# Constants
ACCOUNT_FOLDER = "Account"
LICENSE_FOLDER = "License"
os.makedirs(ACCOUNT_FOLDER, exist_ok=True)
os.makedirs(LICENSE_FOLDER, exist_ok=True)

ACCOUNTS_FILE = os.path.join(ACCOUNT_FOLDER, "accounts.json")
LICENSE_FILE = os.path.join(LICENSE_FOLDER, "keys.json")
GITHUB_REPO_URL = "https://github.com/EleganceApp/Ethereal"
ERROR_LOG = "ethereal_account_error.log"

def log_error(error):
    """Log errors to a file for debugging"""
    with open(ERROR_LOG, 'a') as f:
        f.write(f"{datetime.now()}: {str(error)}\n")

class AccountManager:
    @staticmethod
    def load_accounts():
        try:
            if os.path.exists(ACCOUNTS_FILE):
                with open(ACCOUNTS_FILE, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load accounts: {str(e)}")
            log_error(e)
            return {}

    @staticmethod
    def save_accounts(accounts):
        try:
            with open(ACCOUNTS_FILE, 'w') as f:
                json.dump(accounts, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save accounts: {str(e)}")
            log_error(e)

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def load_licenses():
        try:
            if os.path.exists(LICENSE_FILE):
                with open(LICENSE_FILE, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load licenses: {str(e)}")
            log_error(e)
            return {}

    @staticmethod
    def save_licenses(licenses):
        try:
            with open(LICENSE_FILE, 'w') as f:
                json.dump(licenses, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save licenses: {str(e)}")
            log_error(e)

    @staticmethod
    def validate_license(username):
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
        try:
            self.accounts = AccountManager.load_accounts()
            self.current_user = None
            self.initialize_ui()
        except Exception as e:
            log_error(e)
            messagebox.showerror("Critical Error", f"Failed to initialize application:\n{str(e)}\n\nSee {ERROR_LOG} for details.")
            self.root.destroy()

    def initialize_ui(self):
        """Initialize the main UI components"""
        self.root.title("Ethereal Account Manager v1.0.0")
        self.root.geometry("600x400")
        self.root.configure(bg="#0f1923")
        self.root.resizable(False, False)
        
        # Make sure window appears in foreground
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
        
        # Initialize all UI methods
        self.create_login_screen()
        self.create_profile_screen()
        self.create_license_dialog()
        self.create_register_dialog()
        
        # Show initial screen
        self.show_login_screen()

    def create_login_screen(self):
        """Create all login screen widgets"""
        self.login_frame = tk.Frame(self.root, bg="#0f1923")
        
        # Improved fonts and styling
        title_font = font.Font(family="Arial", size=24, weight="bold")
        label_font = font.Font(family="Segoe UI", size=12)
        entry_font = font.Font(family="Segoe UI", size=12)
        button_font = font.Font(family="Segoe UI", size=11, weight="bold")

        # Header with improved spacing
        header_frame = tk.Frame(self.login_frame, bg="#0f1923")
        header_frame.pack(pady=(0, 30))
        tk.Label(header_frame, text="ETHEREAL ACCOUNTS", 
                fg="#00f2ff", bg="#0f1923", font=title_font).pack()

        # Form frame with better organization
        form_frame = tk.Frame(self.login_frame, bg="#0f1923")
        form_frame.pack(pady=10)

        # Username field with placeholder-like behavior
        tk.Label(form_frame, text="Username:", 
               fg="white", bg="#0f1923", font=label_font).grid(row=0, column=0, sticky="w", pady=5)
        self.username_entry = ttk.Entry(form_frame, width=28, font=entry_font)
        self.username_entry.grid(row=0, column=1, padx=10, pady=5)
        self.username_entry.insert(0, "Enter your username")
        self.username_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.username_entry, "Enter your username"))

        # Password field with show/hide option
        tk.Label(form_frame, text="Password:", 
               fg="white", bg="#0f1923", font=label_font).grid(row=1, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(form_frame, width=28, show="•", font=entry_font)
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Show password checkbox
        self.show_password = tk.BooleanVar()
        ttk.Checkbutton(form_frame, text="Show password", variable=self.show_password,
                       command=self.toggle_password_visibility).grid(row=2, column=1, sticky="w", pady=5)

        # Buttons with consistent styling and spacing
        btn_frame = tk.Frame(self.login_frame, bg="#0f1923")
        btn_frame.pack(pady=20)

        buttons = [
            ("Login", "#00f2ff", "#0f1923", self.login),
            ("Register", "#2a2e35", "white", self.show_register),
            ("Exit", "#d33f49", "white", self.root.quit)
        ]

        for text, bg, fg, cmd in buttons:
            btn = tk.Button(btn_frame, text=text, bg=bg, fg=fg,
                           font=button_font, padx=20, pady=5, command=cmd)
            btn.pack(side=tk.LEFT, padx=10, ipadx=5)

        # Footer with better organization
        footer_frame = tk.Frame(self.login_frame, bg="#0f1923")
        footer_frame.pack(side=tk.BOTTOM, pady=10)
        
        tk.Label(footer_frame, text="© 2025 Ethereal | All Rights Reserved", 
                fg="#00f2ff", bg="#0f1923", font=("Segoe UI", 9)).pack()
        
        elegance_link = tk.Label(footer_frame, text="EleganceApp", 
                               fg="#00f2ff", bg="#0f1923", cursor="hand2", font=("Segoe UI", 9))
        elegance_link.pack()
        elegance_link.bind("<Button-1>", lambda e: webbrowser.open(GITHUB_REPO_URL))
        
        tk.Label(footer_frame, text="v1.0.0", fg="#00f2ff", bg="#0f1923", font=("Segoe UI", 9)).pack()

    def clear_placeholder(self, entry, placeholder):
        """Clear placeholder text when field is clicked"""
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            if entry == self.password_entry:
                entry.config(show="•")

    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.show_password.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="•")

    def create_profile_screen(self):
        """Create all profile screen widgets"""
        self.profile_frame = tk.Frame(self.root, bg="#0f1923")
        
        title_font = font.Font(family="Arial", size=24, weight="bold")
        text_font = font.Font(family="Segoe UI", size=12)
        button_font = font.Font(family="Segoe UI", size=12)

        # Header
        header_frame = tk.Frame(self.profile_frame, bg="#0f1923")
        header_frame.pack(pady=(0, 20))
        self.profile_title = tk.Label(header_frame, text="", 
                fg="#00f2ff", bg="#0f1923", font=title_font)
        self.profile_title.pack()
        tk.Label(header_frame, text="Ethereal v1.0.0", 
                fg="#00f2ff", bg="#0f1923", font=text_font).pack()

        # Account info
        self.info_frame = tk.Frame(self.profile_frame, bg="#0f1923")
        self.info_frame.pack(fill=tk.X, pady=10)

        # License status
        self.license_frame = tk.Frame(self.profile_frame, bg="#0f1923")
        self.license_frame.pack(fill=tk.X, pady=20)
        
        tk.Label(self.license_frame, text="LICENSE STATUS:", 
               fg="white", bg="#0f1923", font=text_font).pack(side=tk.LEFT)
        self.license_status_label = tk.Label(self.license_frame, text="", 
               fg="white", bg="#0f1923", font=text_font)
        self.license_status_label.pack(side=tk.LEFT, padx=10)

        self.add_license_btn = tk.Button(self.license_frame, text="Add License Key", bg="#00f2ff", fg="#0f1923",
                     font=text_font, command=self.show_add_license)
        
        # Main buttons
        self.btn_frame = tk.Frame(self.profile_frame, bg="#0f1923")
        self.btn_frame.pack(fill=tk.X, pady=20)

        tk.Button(self.btn_frame, text="Launch Ethereal", bg="#00f2ff", fg="#0f1923",
                font=button_font, padx=20, command=self.open_main_app).pack(side=tk.LEFT, padx=5)
        tk.Button(self.btn_frame, text="Logout", bg="#2a2e35", fg="white",
                font=button_font, padx=20, command=self.show_login_screen).pack(side=tk.RIGHT, padx=5)

        # Footer
        elegance_link = tk.Label(self.profile_frame, text="EleganceApp", fg="#00f2ff", bg="#0f1923", cursor="hand2")
        elegance_link.pack(side=tk.BOTTOM)
        elegance_link.bind("<Button-1>", lambda e: webbrowser.open(GITHUB_REPO_URL))
        tk.Label(self.profile_frame, text="© 2025 Ethereal | All Rights Reserved", 
                fg="#00f2ff", bg="#0f1923").pack(side=tk.BOTTOM)

    def create_license_dialog(self):
        """Create the license activation dialog"""
        self.license_dialog = tk.Toplevel(self.root)
        self.license_dialog.title("Add License Key")
        self.license_dialog.geometry("300x150")
        self.license_dialog.configure(bg="#0f1923")
        self.license_dialog.resizable(False, False)
        self.license_dialog.withdraw()  # Hide initially
        
        # Content
        tk.Label(self.license_dialog, text="Enter License Key:", 
               fg="#00f2ff", bg="#0f1923").pack(pady=10)
        
        self.license_entry = ttk.Entry(self.license_dialog, width=25)
        self.license_entry.pack(pady=5)

        # Buttons
        btn_frame = tk.Frame(self.license_dialog, bg="#0f1923")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Activate", bg="#00f2ff", fg="#0f1923",
                 command=self.activate_license).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Cancel", bg="#2a2e35", fg="white",
                 command=self.license_dialog.withdraw).pack(side=tk.RIGHT, padx=10)

    def create_register_dialog(self):
        """Create the registration dialog"""
        self.register_dialog = tk.Toplevel(self.root)
        self.register_dialog.title("Register New Account - Ethereal v1.0.0")
        self.register_dialog.geometry("400x350")
        self.register_dialog.configure(bg="#0f1923")
        self.register_dialog.resizable(False, False)
        self.register_dialog.withdraw()  # Hide initially
        
        # Main container
        main_frame = tk.Frame(self.register_dialog, bg="#0f1923")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_font = font.Font(family="Arial", size=16, weight="bold")
        tk.Label(main_frame, text="Create New Account", 
                fg="#00f2ff", bg="#0f1923", font=title_font).pack(pady=(0, 20))
        
        # Form frame
        form_frame = tk.Frame(main_frame, bg="#0f1923")
        form_frame.pack(fill=tk.X)
        
        # Field creation helper
        def create_field(parent, label_text, row, is_password=False):
            tk.Label(parent, text=label_text, fg="white", bg="#0f1923",
                   font=("Segoe UI", 10)).grid(row=row, column=0, sticky="w", pady=5)
            entry = ttk.Entry(parent, width=25, show="•" if is_password else "")
            entry.grid(row=row, column=1, padx=10, pady=5)
            return entry
        
        # Create all fields
        self.reg_username_entry = create_field(form_frame, "Username:", 0)
        self.reg_password_entry = create_field(form_frame, "Password:", 1, True)
        self.reg_confirm_password_entry = create_field(form_frame, "Confirm Password:", 2, True)
        self.reg_email_entry = create_field(form_frame, "Email:", 3)
        self.reg_license_entry = create_field(form_frame, "License Key (optional):", 4)
        
        # Register button
        btn_frame = tk.Frame(main_frame, bg="#0f1923")
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Register", bg="#00f2ff", fg="#0f1923",
                font=("Segoe UI", 12), padx=30, pady=5,
                command=self.register_account).pack()

    def show_login_screen(self):
        """Show the login screen"""
        self.profile_frame.pack_forget()
        self.login_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        self.username_entry.focus_set()

    def show_profile(self):
        """Show the profile screen"""
        self.login_frame.pack_forget()
        
        # Update profile information
        self.profile_title.config(text=f"WELCOME BACK, {self.current_user.upper()}!")
        
        # Clear old info labels
        for widget in self.info_frame.winfo_children():
            widget.destroy()
            
        # Add updated account info
        account_data = self.accounts[self.current_user]
        tk.Label(self.info_frame, text=f"Email: {account_data['email']}", 
               fg="white", bg="#0f1923").pack(anchor="w")
        tk.Label(self.info_frame, text=f"Member since: {account_data['created']}", 
               fg="white", bg="#0f1923").pack(anchor="w")

        # Update license status
        license_status = AccountManager.validate_license(self.current_user)
        status_color = "#00ff00" if license_status else "#ff0000"
        status_text = "ACTIVE" if license_status else "INACTIVE"
        self.license_status_label.config(text=status_text, fg=status_color)
        
        # Show/hide add license button
        if license_status:
            self.add_license_btn.pack_forget()
        else:
            self.add_license_btn.pack(side=tk.RIGHT, padx=10)
        
        self.profile_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)

    def show_register(self):
        """Show the registration dialog"""
        # Clear all fields
        for entry in [self.reg_username_entry, self.reg_password_entry, 
                     self.reg_confirm_password_entry, self.reg_email_entry, 
                     self.reg_license_entry]:
            entry.delete(0, tk.END)
        
        # Show and position dialog
        self.register_dialog.deiconify()
        self.register_dialog.grab_set()
        
        # Center dialog
        self.register_dialog.update_idletasks()
        width = self.register_dialog.winfo_width()
        height = self.register_dialog.winfo_height()
        x = (self.register_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.register_dialog.winfo_screenheight() // 2) - (height // 2)
        self.register_dialog.geometry(f"+{x}+{y}")
        
        self.reg_username_entry.focus_set()

    def show_add_license(self):
        """Show the license activation dialog"""
        self.license_entry.delete(0, tk.END)
        self.license_dialog.deiconify()
        self.license_dialog.grab_set()
        self.license_entry.focus_set()
        
        # Center dialog
        self.license_dialog.update_idletasks()
        width = self.license_dialog.winfo_width()
        height = self.license_dialog.winfo_height()
        x = (self.license_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.license_dialog.winfo_screenheight() // 2) - (height // 2)
        self.license_dialog.geometry(f"+{x}+{y}")

    def register_account(self):
        """Handle account registration"""
        username = self.reg_username_entry.get().strip()
        password = self.reg_password_entry.get()
        confirm_password = self.reg_confirm_password_entry.get()
        email = self.reg_email_entry.get().strip()
        license_key = self.reg_license_entry.get().strip()

        # Validate inputs
        if not username or not password or not confirm_password or not email:
            messagebox.showerror("Error", "All fields except License Key are required")
            return
            
        if len(username) < 4:
            messagebox.showerror("Error", "Username must be at least 4 characters")
            return
            
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return
            
        if len(password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters")
            return
            
        if "@" not in email or "." not in email:
            messagebox.showerror("Error", "Please enter a valid email address")
            return
            
        if username in self.accounts:
            messagebox.showerror("Error", "Username already exists")
            return
            
        # Create new account
        try:
            hashed_pw = AccountManager.hash_password(password)
            self.accounts[username] = {
                'password': hashed_pw,
                'email': email,
                'created': datetime.now().strftime("%Y-%m-%d"),
                'license_key': license_key if license_key else None
            }
            
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
            
            AccountManager.save_accounts(self.accounts)
            messagebox.showinfo("Success", "Account created successfully!")
            self.register_dialog.withdraw()
            
            # Auto-login the new user
            self.current_user = username
            self.show_profile()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create account:\n{str(e)}")
            log_error(e)

    def activate_license(self):
        """Activate the entered license key"""
        key = self.license_entry.get().strip()
        if not key:
            messagebox.showerror("Error", "Please enter a license key")
            return
        
        try:
            licenses = AccountManager.load_licenses()
            licenses[self.current_user] = {
                'key': key,
                'valid': True,
                'activated': datetime.now().strftime("%Y-%m-%d"),
                'expiry': (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
            }
            AccountManager.save_licenses(licenses)
            self.accounts[self.current_user]['license_key'] = key
            AccountManager.save_accounts(self.accounts)
            self.license_dialog.withdraw()
            self.show_profile()  # Refresh to show new status
        except Exception as e:
            messagebox.showerror("Error", f"Failed to activate license:\n{str(e)}")
            log_error(e)

    def login(self):
        """Handle login attempt"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return

        if username in self.accounts:
            hashed_pw = AccountManager.hash_password(password)
            if self.accounts[username]['password'] == hashed_pw:
                self.current_user = username
                self.show_profile()
            else:
                messagebox.showerror("Error", "Invalid password")
        else:
            messagebox.showerror("Error", "Account not found")

    def open_main_app(self):
        """Launch the main Ethereal application"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            ethereal_path = os.path.join(script_dir, "Ethereal.pyw")
            
            if not os.path.exists(ethereal_path):
                messagebox.showerror("Error", f"Main application not found at:\n{ethereal_path}")
                return
            
            subprocess.Popen([sys.executable, ethereal_path])
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch application:\n{str(e)}")
            log_error(e)

def main():
    try:
        root = tk.Tk()
        app = EtherealAccountApp(root)
        
        # Center the window on screen
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'+{x}+{y}')
        
        root.mainloop()
    except Exception as e:
        log_error(e)
        error_root = tk.Tk()
        error_root.withdraw()
        messagebox.showerror("Critical Error", 
            f"Application failed to start:\n{str(e)}\n\n"
            f"See {ERROR_LOG} for details.\n\n"
            "Try running from command line with:\npython EtherealAccount.pyw")
        error_root.destroy()

if __name__ == "__main__":
    # Set working directory correctly
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
    else:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    main()