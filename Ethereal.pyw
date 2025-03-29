import tkinter as tk
from tkinter import messagebox, font
import os
from datetime import datetime
import subprocess
import re

class LicenseManager:
    @staticmethod
    def check_license():
        if not os.path.exists("License/expiration_time.txt"):
            return False
        with open("License/expiration_time.txt", "r") as f:
            expiry_str = f.read().strip()
        try:
            expiry_time = datetime.strptime(expiry_str, "%Y%m%d%H%M")
            return datetime.now() < expiry_time
        except:
            return False

    @staticmethod
    def get_remaining_time():
        with open("License/expiration_time.txt", "r") as f:
            expiry_str = f.read().strip()
        expiry_time = datetime.strptime(expiry_str, "%Y%m%d%H%M")
        return expiry_time - datetime.now()

class KeyAuthWindow:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        if LicenseManager.check_license():
            self.show_license_active_warning()
            
    def setup_ui(self):
        self.root.title("Ethereal v1.0.0 | License Verification")
        self.root.geometry("450x350")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f1923")

        # Main container with perfect spacing
        main_frame = tk.Frame(self.root, bg="#0f1923")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=15)

        # Header section with perfect vertical rhythm
        tk.Label(main_frame, text="ETHEREAL",
                fg="#00f2ff", bg="#0f1923",
                font=("Arial", 24, "bold")).pack(pady=(0, 5))
        
        tk.Label(main_frame, text="LICENSE VERIFICATION",
                fg="#ffffff", bg="#0f1923",
                font=("Segoe UI", 16, "bold")).pack()
        
        # Version label with subtle styling
        tk.Label(main_frame, text="v1.0.0",
                fg="#7f8c8d", bg="#0f1923",
                font=("Arial", 10)).pack(pady=(0, 20))

        # Divider line
        tk.Frame(main_frame, height=1, bg="#1e2b3a").pack(fill=tk.X, pady=(0, 20))

        # Key entry field
        self.key_entry = tk.Entry(main_frame, width=28,
                                font=("Segoe UI", 12),
                                relief=tk.FLAT,
                                highlightthickness=1,
                                highlightcolor="#00f2ff",
                                highlightbackground="#1e2b3a")
        self.key_entry.pack(ipady=8, pady=(0, 15))

        # Verify button with professional styling
        self.verify_btn = tk.Button(
            main_frame, text="VERIFY KEY", 
            bg="#00f2ff", fg="#0f1923",
            activebackground="#00c8d7",
            borderwidth=0,
            padx=30, pady=12,
            font=("Segoe UI", 12, "bold"),
            command=self.verify_key
        )
        self.verify_btn.pack(fill=tk.X, padx=50, pady=(0, 20))

        # Copyright footer - subtle and professional
        copyright_frame = tk.Frame(main_frame, bg="#0f1923")
        copyright_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        tk.Label(copyright_frame, 
               text="© 2025 Ethereal | All Rights Reserved",
               fg="#555555", bg="#0f1923",
               font=("Segoe UI", 8)).pack()

    def show_license_active_warning(self):
        remaining = LicenseManager.get_remaining_time()
        msg = f"License is already active!\n\nTime remaining: {remaining.days}d {remaining.seconds//3600}h {(remaining.seconds//60)%60}m"
        if messagebox.askyesno("License Active", msg + "\n\nDo you want to continue anyway?"):
            self.start_application()
        else:
            self.root.destroy()

    def verify_key(self):
        entered_key = self.key_entry.get().strip().upper()
        if not re.match(r"^ET-[A-Z]{4}-\d{4}-[A-Z0-9]{4}$", entered_key):
            messagebox.showerror("Invalid Format", "Key must be in ET-XXXX-XXXX-XXXX format")
            return
        if not os.path.exists("License/license_key.txt") or not os.path.exists("License/expiration_time.txt"):
            messagebox.showerror("Error", "License files not found in License folder")
            return
        try:
            with open("License/license_key.txt", "r") as f:
                stored_key = f.read().strip()
            with open("License/expiration_time.txt", "r") as f:
                expiry_str = f.read().strip()
            if entered_key != stored_key:
                messagebox.showerror("Invalid Key", "The entered key does not match")
                return
            expiry_time = datetime.strptime(expiry_str, "%Y%m%d%H%M")
            if datetime.now() > expiry_time:
                messagebox.showerror("Expired", "License has expired")
                try:
                    os.remove("License/license_key.txt")
                    os.remove("License/expiration_time.txt")
                except:
                    pass
                return
            self.start_application(expiry_str)
        except Exception as e:
            messagebox.showerror("Error", f"Verification failed: {str(e)}")

    def start_application(self, expiry_str=None):
        if not expiry_str:
            with open("License/expiration_time.txt", "r") as f:
                expiry_str = f.read().strip()
        self.root.destroy()
        MainMenu(tk.Tk(), expiry_str)

class MainMenu:
    def __init__(self, root, expiry_str):
        self.root = root
        self.expiry_time = datetime.strptime(expiry_str, "%Y%m%d%H%M")
        self.setup_ui()
        self.update_timer()
        self.check_license_validity()

    def setup_ui(self):
        self.root.title("Ethereal Main Menu")
        self.root.geometry("800x600")
        self.root.configure(bg="#0f1923")
        tk.Label(
            self.root, text="WELCOME TO ETHEREAL",
            fg="#00f2ff", bg="#0f1923",
            font=("Arial", 28, "bold")
        ).pack(pady=50)
        self.timer_label = tk.Label(
            self.root, text="", fg="#00ff00", 
            bg="#0f1923", font=("Segoe UI", 18, "bold")
        )
        self.timer_label.pack(pady=20)

    def update_timer(self):
        remaining = self.expiry_time - datetime.now()
        if remaining.total_seconds() > 0:
            self.timer_label.config(
                text=f"License valid for: {remaining.days}d {remaining.seconds//3600}h {(remaining.seconds//60)%60}m"
            )
            self.root.after(1000, self.update_timer)
        else:
            self.handle_expiry()

    def check_license_validity(self):
        if datetime.now() >= self.expiry_time:
            self.handle_expiry()
        else:
            self.root.after(60000, self.check_license_validity)

    def handle_expiry(self):
        try:
            os.remove("License/license_key.txt")
            os.remove("License/expiration_time.txt")
        except:
            pass
        messagebox.showwarning("Expired", "Your license has expired")
        self.root.destroy()
        subprocess.Popen(["pythonw", __file__], shell=True)

if __name__ == "__main__":
    if not os.path.exists("License"):
        os.makedirs("License")
    if LicenseManager.check_license():
        root = tk.Tk()
        with open("License/expiration_time.txt", "r") as f:
            expiry_str = f.read().strip()
        MainMenu(root, expiry_str)
        root.mainloop()
    else:
        root = tk.Tk()
        KeyAuthWindow(root)
        root.mainloop()
