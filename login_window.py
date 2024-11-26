import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
from db_config import create_connection
from admin.admin_dashboard import AdminDashboard
from user.user_dashboard import UserDashboard


class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gym Management System")
        self.root.geometry("500x700")
        self.root.resizable(False, False)

        # Apply the Sun Valley theme manually
        self.apply_sun_valley_theme()

        self.style = ttk.Style()
        self.style.configure('TButton', padding=5, font=('Helvetica', 12, 'bold'))
        self.style.configure('TLabel', font=('Helvetica', 12))
        self.style.configure('Header.TLabel', font=('Helvetica', 18, 'bold'))

        self.create_widgets()

    def apply_sun_valley_theme(self):
        """Manually load the Sun Valley theme"""
        try:
            self.root.tk.call("source", "sv.tcl")  # Ensure the path to sv.tcl is correct
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load theme: {str(e)}")
            return

    def create_widgets(self):
        header = ttk.Label(self.root, text="Gym Management System", style='Header.TLabel')
        header.pack(pady=30)

        # Notebook for Login/Register tabs
        self.tab_control = ttk.Notebook(self.root, style='TNotebook')
        self.tab_control.pack(expand=1, fill="both", padx=20, pady=20)

        # Login Tab
        self.login_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.login_tab, text='Login')
        self.create_login_tab()

        # Register Tab
        self.register_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.register_tab, text='Register')
        self.create_register_tab()

        footer = ttk.Label(self.root, text="© 2024 Gym Management System", font=('Helvetica', 10, 'italic'))
        footer.pack(side="bottom", pady=10)

    def create_login_tab(self):
        frame = ttk.Frame(self.login_tab, padding=20)
        frame.pack(expand=True, fill='both')

        ttk.Label(frame, text="Login As:").pack(pady=10, anchor='w')
        self.login_user_type = ttk.Combobox(frame, values=['User', 'Admin'], state='readonly', font=('Helvetica', 12))
        self.login_user_type.set('User')
        self.login_user_type.pack(pady=5)

        ttk.Label(frame, text="Username:").pack(pady=10, anchor='w')
        self.login_username = ttk.Entry(frame, font=('Helvetica', 12))
        self.login_username.pack(pady=5)

        ttk.Label(frame, text="Password:").pack(pady=10, anchor='w')
        self.login_password = ttk.Entry(frame, show="*", font=('Helvetica', 12))
        self.login_password.pack(pady=5)

        ttk.Button(frame, text="Login", command=self.login).pack(pady=30)

    def create_register_tab(self):
        frame = ttk.Frame(self.register_tab, padding=20)
        frame.pack(expand=True, fill='both')

        ttk.Label(frame, text="Register As:").pack(pady=10, anchor='w')
        self.register_user_type = ttk.Combobox(frame, values=['User', 'Admin'], state='readonly', font=('Helvetica', 12))
        self.register_user_type.set('User')
        self.register_user_type.pack(pady=5)

        ttk.Label(frame, text="Username:").pack(pady=10, anchor='w')
        self.register_username = ttk.Entry(frame, font=('Helvetica', 12))
        self.register_username.pack(pady=5)

        ttk.Label(frame, text="Email:").pack(pady=10, anchor='w')
        self.register_email = ttk.Entry(frame, font=('Helvetica', 12))
        self.register_email.pack(pady=5)

        ttk.Label(frame, text="Password:").pack(pady=10, anchor='w')
        self.register_password = ttk.Entry(frame, show="*", font=('Helvetica', 12))
        self.register_password.pack(pady=5)

        ttk.Label(frame, text="Confirm Password:").pack(pady=10, anchor='w')
        self.register_confirm_password = ttk.Entry(frame, show="*", font=('Helvetica', 12))
        self.register_confirm_password.pack(pady=5)

        ttk.Button(frame, text="Register", command=self.register).pack(pady=30)

    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self):
        username = self.login_username.get()
        password = self.hash_password(self.login_password.get())
        user_type = self.login_user_type.get().lower()

        try:
            conn = create_connection()
            cursor = conn.cursor(dictionary=True)

            if user_type == 'admin':
                query = "SELECT * FROM ADMIN WHERE username = %s AND password = %s"
            else:
                query = "SELECT * FROM USER WHERE username = %s AND password = %s"

            cursor.execute(query, (username, password))
            user = cursor.fetchone()

            if user:
                self.root.withdraw()
                if user_type == 'admin':
                    AdminDashboard(self.root, user)
                else:
                    UserDashboard(self.root, user)
            else:
                messagebox.showerror("Error", "Invalid username or password")

        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def register(self):
        user_type = self.register_user_type.get().lower()
        username = self.register_username.get()
        email = self.register_email.get()
        password = self.register_password.get()
        confirm_password = self.register_confirm_password.get()

        if not all([username, email, password, confirm_password]):
            messagebox.showerror("Error", "All fields are required!")
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            return

        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters!")
            return

        try:
            conn = create_connection()
            cursor = conn.cursor()

            table = "ADMIN" if user_type == "admin" else "USER"
            cursor.execute(f"SELECT username FROM {table} WHERE username = %s", (username,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Username already exists!")
                return

            cursor.execute(f"SELECT email FROM {table} WHERE email = %s", (email,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Email already registered!")
                return

            hashed_password = self.hash_password(password)
            cursor.execute(
                f"INSERT INTO {table} (username, email, password) VALUES (%s, %s, %s)",
                (username, email, hashed_password)
            )
            conn.commit()

            messagebox.showinfo("Success", f"{user_type.capitalize()} registration successful! Please login.")
            self.tab_control.select(0)

        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = LoginWindow()
    app.run()
