import tkinter as tk
from tkinter import messagebox, font
import os
from datetime import datetime
import subprocess
import re  # Added missing import

class LicenseManager:
    @staticmethod
    def check_license():
        """Check license validity based on expiration time"""
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
        """Calculate remaining license time"""
        with open("License/expiration_time.txt", "r") as f:
            expiry_str = f.read().strip()
        expiry_time = datetime.strptime(expiry_str, "%Y%m%d%H%M")
        return expiry_time - datetime.now()

class KeyAuthWindow:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        
        # Check for existing valid license
        if LicenseManager.check_license():
            self.show_license_active_warning()
            
    def show_license_active_warning(self):
        remaining = LicenseManager.get_remaining_time()
        msg = f"License is already active!\n\nTime remaining: {remaining.days}d {remaining.seconds//3600}h {(remaining.seconds//60)%60}m"
        if messagebox.askyesno("License Active", msg + "\n\nDo you want to continue anyway?"):
            self.start_application()
        else:
            self.root.destroy()

    def setup_ui(self):
        self.root.title("Ethereal | License Verification")
        self.root.geometry("450x350")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f1923")

        # Fonts
        self.header_font = font.Font(family="Arial", size=24, weight="bold")
        self.title_font = font.Font(family="Segoe UI", size=16, weight="bold")
        self.button_font = font.Font(family="Segoe UI", size=12, weight="bold")

        # Main frame
        self.main_frame = tk.Frame(self.root, bg="#0f1923")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)

        # UI Elements
        tk.Label(self.main_frame, text="ETHEREAL", fg="#00f2ff", bg="#0f1923", 
                font=self.header_font).pack(pady=(0, 10))
        tk.Label(self.main_frame, text="LICENSE VERIFICATION", fg="#ffffff", 
                bg="#0f1923", font=self.title_font).pack(pady=(0, 25))

        self.key_entry = tk.Entry(self.main_frame, width=28, 
                                font=font.Font(family="Segoe UI", size=12))
        self.key_entry.pack(ipady=8, pady=10)

        self.verify_btn = tk.Button(
            self.main_frame, text="VERIFY KEY", bg="#00f2ff", fg="#0f1923", bd=0,
            padx=20, pady=10, font=self.button_font, command=self.verify_key
        )
        self.verify_btn.pack(fill=tk.X, padx=50, pady=15)

        tk.Label(self.main_frame, text="© 2025 Ethereal | All Rights Reserved", 
                fg="#555555", bg="#0f1923", font=font.Font(family="Segoe UI", size=8)
                ).pack(side=tk.BOTTOM, pady=10)

    def verify_key(self):
        """Complete verification method"""
        entered_key = self.key_entry.get().strip().upper()
        
        # Check key format
        if not re.match(r"^ET-[A-Z]{4}-\d{4}-[A-Z0-9]{4}$", entered_key):
            messagebox.showerror("Invalid Format", "Key must be in ET-XXXX-XXXX-XXXX format")
            return
            
        # Check if license files exist
        if not os.path.exists("License/license_key.txt") or not os.path.exists("License/expiration_time.txt"):
            messagebox.showerror("Error", "License files not found in License folder")
            return
            
        try:
            # Read stored key
            with open("License/license_key.txt", "r") as f:
                stored_key = f.read().strip()
                
            # Read expiration time
            with open("License/expiration_time.txt", "r") as f:
                expiry_str = f.read().strip()
                
            # Verify key match
            if entered_key != stored_key:
                messagebox.showerror("Invalid Key", "The entered key does not match")
                return
                
            # Verify expiry
            expiry_time = datetime.strptime(expiry_str, "%Y%m%d%H%M")
            if datetime.now() > expiry_time:
                messagebox.showerror("Expired", "License has expired")
                try:
                    os.remove("License/license_key.txt")
                    os.remove("License/expiration_time.txt")
                except:
                    pass
                return
                
            # Success - launch main app
            self.start_application(expiry_str)
            
        except Exception as e:
            messagebox.showerror("Error", f"Verification failed: {str(e)}")

    def start_application(self, expiry_str=None):
        """Start main application with persistent license check"""
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
        
        # Start background license checker
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
        """Background check that runs even if window is closed"""
        if datetime.now() >= self.expiry_time:
            self.handle_expiry()
        else:
            self.root.after(60000, self.check_license_validity)

    def handle_expiry(self):
        """Handle license expiration"""
        try:
            os.remove("License/license_key.txt")
            os.remove("License/expiration_time.txt")
        except:
            pass
            
        messagebox.showwarning("Expired", "Your license has expired")
        self.root.destroy()
        subprocess.Popen(["pythonw", __file__], shell=True)

if __name__ == "__main__":
    # Create License folder if it doesn't exist
    if not os.path.exists("License"):
        os.makedirs("License")
    
    # Check license before showing UI
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