import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from db_config import create_connection
import calendar


class UserDashboard:
    def __init__(self, parent, user_data):
        self.parent = parent  # Parent window (login window)
        self.user_data = user_data

        # Create main window
        self.root = tk.Toplevel()
        self.root.title(f"User Dashboard - {user_data['username']}")
        self.root.geometry("1000x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Configure styles
        self.style = ttk.Style()
        self.style.configure('Header.TLabel', font=('Helvetica', 14, 'bold'))
        self.style.configure('Info.TLabel', font=('Helvetica', 12))

        self.create_widgets()
        self.load_user_data()

    def create_widgets(self):
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)

        # Create tabs
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.subscription_tab = ttk.Frame(self.notebook)
        self.attendance_tab = ttk.Frame(self.notebook)
        self.payment_tab = ttk.Frame(self.notebook)
        self.classes_tab = ttk.Frame(self.notebook)  # New tab for classes

        self.notebook.add(self.dashboard_tab, text='Dashboard')
        self.notebook.add(self.subscription_tab, text='Subscription')
        self.notebook.add(self.attendance_tab, text='Attendance')
        self.notebook.add(self.payment_tab, text='Payment History')
        self.notebook.add(self.classes_tab, text='Classes')  # Add the new classes tab

        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)

        # Setup each tab
        self.setup_dashboard_tab()
        self.setup_subscription_tab()
        self.setup_attendance_tab()
        self.setup_payment_tab()
        self.setup_classes_tab()  # Set up the new classes tab

    def setup_dashboard_tab(self):
        # User Info Frame
        info_frame = ttk.LabelFrame(self.dashboard_tab, text="User Information", padding=10)
        info_frame.pack(fill='x', padx=10, pady=5)

        self.balance_label = ttk.Label(info_frame, text="Balance: ", style='Info.TLabel')
        self.balance_label.pack(anchor='w')

        # Active Subscription Frame
        sub_frame = ttk.LabelFrame(self.dashboard_tab, text="Active Subscription", padding=10)
        sub_frame.pack(fill='x', padx=10, pady=5)

        self.subscription_status = ttk.Label(sub_frame, text="No active subscription", style='Info.TLabel')
        self.subscription_status.pack(anchor='w')

        self.remaining_days = ttk.Label(sub_frame, text="", style='Info.TLabel')
        self.remaining_days.pack(anchor='w')

    def setup_subscription_tab(self):
        # New Subscription Frame
        sub_frame = ttk.LabelFrame(self.subscription_tab, text="New Subscription", padding=10)
        sub_frame.pack(fill='x', padx=10, pady=5)

        # Date Selection
        ttk.Label(sub_frame, text="Start Date:").pack(anchor='w', pady=5)
        self.start_date = DateEntry(sub_frame, width=12, background='darkblue',
                                    foreground='white', borderwidth=2)
        self.start_date.pack(anchor='w')

        ttk.Label(sub_frame, text="End Date:").pack(anchor='w', pady=5)
        self.end_date = DateEntry(sub_frame, width=12, background='darkblue',
                                  foreground='white', borderwidth=2)
        self.end_date.pack(anchor='w')

        # Calculate Button
        ttk.Button(sub_frame, text="Calculate Cost",
                   command=self.calculate_subscription_cost).pack(pady=10)

        self.cost_label = ttk.Label(sub_frame, text="")
        self.cost_label.pack()

        # Purchase Button
        ttk.Button(sub_frame, text="Purchase Subscription",
                   command=self.purchase_subscription).pack(pady=10)

    def setup_attendance_tab(self):
        # Today's Attendance Frame
        attendance_frame = ttk.LabelFrame(self.attendance_tab, text="Mark Attendance", padding=10)
        attendance_frame.pack(fill='x', padx=10, pady=5)

        self.attendance_status = ttk.Label(attendance_frame, text="")
        self.attendance_status.pack()

        ttk.Button(attendance_frame, text="Mark Present",
                   command=self.mark_attendance).pack(pady=10)

        # Attendance History
        history_frame = ttk.LabelFrame(self.attendance_tab, text="Attendance History", padding=10)
        history_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Treeview for attendance history
        self.attendance_tree = ttk.Treeview(history_frame, columns=('Date', 'Status'),
                                            show='headings')
        self.attendance_tree.heading('Date', text='Date')
        self.attendance_tree.heading('Status', text='Status')
        self.attendance_tree.pack(fill='both', expand=True)

    def setup_payment_tab(self):
        # Payment History
        self.payment_tree = ttk.Treeview(self.payment_tab,
                                         columns=('Date', 'Amount', 'Type', 'Status'),
                                         show='headings')
        self.payment_tree.heading('Date', text='Date')
        self.payment_tree.heading('Amount', text='Amount')
        self.payment_tree.heading('Type', text='Type')
        self.payment_tree.heading('Status', text='Status')
        self.payment_tree.pack(fill='both', expand=True, padx=10, pady=5)


    def setup_classes_tab(self):
        # Frame for enrolled classes
        enrolled_classes_frame = ttk.LabelFrame(self.classes_tab, text="Enrolled Classes", padding=10)
        enrolled_classes_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Treeview to display enrolled classes
        self.enrolled_classes_tree = ttk.Treeview(enrolled_classes_frame,
                                                  columns=('Name', 'Enrollment Date', 'Payment Status'), show='headings')
        self.enrolled_classes_tree.heading('Name', text='Class Name')
        self.enrolled_classes_tree.heading('Enrollment Date', text='Enrollment Date')
        self.enrolled_classes_tree.heading('Payment Status', text='Payment Status')
        self.enrolled_classes_tree.pack(fill='both', expand=True)

        # Button to refresh enrolled classes
        ttk.Button(enrolled_classes_frame, text="Refresh Enrolled Classes", command=self.load_enrolled_classes).pack(
            pady=10)

        # Frame for viewing available classes
        view_class_frame = ttk.LabelFrame(self.classes_tab, text="Available Classes", padding=10)
        view_class_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Treeview to display available classes
        self.classes_tree = ttk.Treeview(view_class_frame,
                                         columns=('ID', 'Name', 'Start Date', 'End Date', 'Price', 'Active'),
                                         show='headings')
        self.classes_tree.heading('ID', text='Class ID')
        self.classes_tree.heading('Name', text='Class Name')
        self.classes_tree.heading('Start Date', text='Start Date')
        self.classes_tree.heading('End Date', text='End Date')
        self.classes_tree.heading('Price', text='Price')
        self.classes_tree.heading('Active', text='Active')
        self.classes_tree.pack(fill='both', expand=True)

        # Button to enroll in a class
        ttk.Button(view_class_frame, text="Enroll in Class", command=self.enroll_in_class).pack(pady=10)

        # Load classes
        self.load_classes_data()


    def load_classes_data(self):
        try:
            conn = create_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                    SELECT class_id, class_name, start_date, end_date, price
                    FROM CLASSES
                    WHERE is_active = TRUE
                """)
            classes = cursor.fetchall()

            self.classes_tree.delete(*self.classes_tree.get_children())
            for class_info in classes:
                self.classes_tree.insert('', 'end', values=(
                    class_info['class_id'],
                    class_info['class_name'],
                    class_info['start_date'],
                    class_info['end_date'],
                    f"{class_info['price']:.2f}"
                ))

            cursor.close()
            conn.close()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load classes: {str(e)}")


    def enroll_in_class(self):
        selected_item = self.classes_tree.selection()
        if selected_item:
            class_data = self.classes_tree.item(selected_item, "values")
            class_id = class_data[0]
            class_price = float(class_data[4])
            self.enroll_user_in_class(class_id, class_price)
        else:
            messagebox.showwarning("No Selection", "Please select a class to enroll in.")


    def enroll_user_in_class(self, class_id, class_price):
        try:
            conn = create_connection()
            cursor = conn.cursor()

            # Check if user is already enrolled in this class
            cursor.execute("""
                    SELECT * FROM ENROLLMENT
                    WHERE user_id = %s AND class_id = %s AND payment_status = 'pending'
                """, (self.user_data['user_id'], class_id))
            if cursor.fetchone():
                messagebox.showinfo("Info", "You are already enrolled in this class.")
                return

            # Insert enrollment record
            cursor.execute("""
                    INSERT INTO ENROLLMENT (user_id, class_id)
                    VALUES (%s, %s)
                """, (self.user_data['user_id'], class_id))

            # Create a payment record
            cursor.execute("""
                    INSERT INTO PAYMENT (user_id, class_id, amount, payment_status)
                    VALUES (%s, %s, %s, 'pending')
                """, (self.user_data['user_id'], class_id, class_price))

            conn.commit()
            messagebox.showinfo("Success", "You have successfully enrolled in the class. Please make the payment.")
            self.load_user_data()  # Refresh user data

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to enroll in class: {str(e)}")
        finally:
            cursor.close()
            conn.close()


    def pay_for_class(self, class_id, amount):
        try:
            conn = create_connection()
            cursor = conn.cursor()

            cursor.execute("""
                    UPDATE PAYMENT
                    SET payment_status = 'completed'
                    WHERE user_id = %s AND class_id = %s AND payment_status = 'pending'
                """, (self.user_data['user_id'], class_id))

            # Update class enrollment payment status
            cursor.execute("""
                    UPDATE ENROLLMENT
                    SET payment_status = 'completed'
                    WHERE user_id = %s AND class_id = %s
                """, (self.user_data['user_id'], class_id))

            # Update user balance
            cursor.execute("""
                    UPDATE USER
                    SET wallet_balance = wallet_balance - %s
                    WHERE user_id = %s
                """, (amount, self.user_data['user_id']))

            # Update admin balance
            cursor.execute("""
                    UPDATE ADMIN
                    SET wallet_balance = wallet_balance + %s
                    WHERE admin_id = 1
                """, (amount,))

            conn.commit()
            messagebox.showinfo("Success", "Payment completed successfully!")
            self.load_user_data()  # Refresh user data

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to make payment: {str(e)}")
        finally:
            cursor.close()
            conn.close()


    def load_enrolled_classes(self):
        try:
            conn = create_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                    SELECT c.class_name, e.enrollment_date, e.payment_status
                    FROM ENROLLMENT e
                    JOIN CLASSES c ON e.class_id = c.class_id
                    WHERE e.user_id = %s
                """, (self.user_data['user_id'],))

            enrolled_classes = cursor.fetchall()

            self.enrolled_classes_tree.delete(*self.enrolled_classes_tree.get_children())
            for record in enrolled_classes:
                self.enrolled_classes_tree.insert('', 'end', values=(
                    record['class_name'],
                    record['enrollment_date'],
                    record['payment_status']
                ))

            cursor.close()
            conn.close()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load enrolled classes: {str(e)}")


    def load_user_data(self):
        try:
            conn = create_connection()
            cursor = conn.cursor(dictionary=True)

            # Load balance
            cursor.execute("SELECT wallet_balance FROM USER WHERE user_id = %s",
                           (self.user_data['user_id'],))
            balance = cursor.fetchone()['wallet_balance']
            self.balance_label.config(text=f"Balance: {balance:.2f} units")

            # Load active subscription
            cursor.execute("""
                    SELECT * FROM SUBSCRIPTION 
                    WHERE user_id = %s AND is_active = TRUE 
                    AND status = 'active'
                    ORDER BY end_date DESC LIMIT 1
                """, (self.user_data['user_id'],))
            subscription = cursor.fetchone()

            if subscription:
                self.subscription_status.config(
                    text=f"Active until: {subscription['end_date']}")
                self.remaining_days.config(
                    text=f"Remaining days: {subscription['remaining_days']}")

            # Load attendance history
            cursor.execute("""
                    SELECT attendance_date, is_present 
                    FROM ATTENDANCE 
                    WHERE user_id = %s 
                    ORDER BY attendance_date DESC
                """, (self.user_data['user_id'],))

            self.attendance_tree.delete(*self.attendance_tree.get_children())
            for record in cursor.fetchall():
                status = "Present" if record['is_present'] else "Absent"
                self.attendance_tree.insert('', 'end', values=(
                    record['attendance_date'], status))

            # Load payment history
            cursor.execute("""
                    SELECT transaction_date, amount, transaction_type, status 
                    FROM TRANSACTION 
                    WHERE user_id = %s 
                    ORDER BY transaction_date DESC
                """, (self.user_data['user_id'],))

            self.payment_tree.delete(*self.payment_tree.get_children())
            for record in cursor.fetchall():
                self.payment_tree.insert('', 'end', values=(
                    record['transaction_date'],
                    f"{record['amount']:.2f}",
                    record['transaction_type'],
                    record['status']
                ))

            cursor.close()
            conn.close()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load user data: {str(e)}")


    def calculate_subscription_cost(self):
        start = self.start_date.get_date()
        end = self.end_date.get_date()

        if end < start:
            messagebox.showerror("Error", "End date must be after start date")
            return

        days = (end - start).days + 1
        cost = days * 1.0  # 1 unit per day

        self.cost_label.config(text=f"Total Cost: {cost:.2f} units")


    def purchase_subscription(self):
        try:
            conn = create_connection()
            cursor = conn.cursor()

            start_date = self.start_date.get_date()
            end_date = self.end_date.get_date()
            days = (end_date - start_date).days + 1
            cost = days * 1.0

            # Check for active subscription
            cursor.execute("""
                    SELECT * FROM SUBSCRIPTION 
                    WHERE user_id = %s AND is_active = TRUE 
                    AND status = 'active'
                    AND (start_date <= %s AND end_date >= %s)
                """, (self.user_data['user_id'], end_date, start_date))

            if cursor.fetchone():
                messagebox.showerror("Error", "You already have an active subscription for this period")
                return

            # Check balance
            cursor.execute("SELECT wallet_balance FROM USER WHERE user_id = %s",
                           (self.user_data['user_id'],))
            balance = cursor.fetchone()[0]

            if balance < cost:
                messagebox.showerror("Error", "Insufficient balance")
                return

            # Start transaction
            cursor.execute("START TRANSACTION")

            # Create subscription
            cursor.execute("""
                    INSERT INTO SUBSCRIPTION 
                    (user_id, start_date, end_date, remaining_days, is_active, status)
                    VALUES (%s, %s, %s, %s, TRUE, 'active')
                """, (self.user_data['user_id'], start_date, end_date, days))

            subscription_id = cursor.lastrowid

            # Create transaction
            cursor.execute("""
                    INSERT INTO TRANSACTION 
                    (user_id, subscription_id, amount, transaction_type, status)
                    VALUES (%s, %s, %s, 'subscription_purchase', 'completed')
                """, (self.user_data['user_id'], subscription_id, cost))

            # Update user balance
            cursor.execute("""
                    UPDATE USER SET wallet_balance = wallet_balance - %s 
                    WHERE user_id = %s
                """, (cost, self.user_data['user_id']))

            # Update admin balance
            cursor.execute("""
                    UPDATE ADMIN SET wallet_balance = wallet_balance + %s 
                    WHERE admin_id = 1
                """, (cost,))

            conn.commit()
            messagebox.showinfo("Success", "Subscription purchased successfully!")
            self.load_user_data()  # Refresh display

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to purchase subscription: {str(e)}")
        finally:
            cursor.close()
            conn.close()


    def mark_attendance(self):
        try:
            conn = create_connection()
            cursor = conn.cursor(dictionary=True)

        # Check active subscription
            cursor.execute("""
                    SELECT subscription_id FROM SUBSCRIPTION 
                    WHERE user_id = %s AND is_active = TRUE 
                    AND status = 'active'
                    AND CURRENT_DATE BETWEEN start_date AND end_date
                """, (self.user_data['user_id'],))

            subscription = cursor.fetchone()
            if not subscription:
                messagebox.showerror("Error", "No active subscription found")
                return

        # Check if attendance already marked
            today = datetime.now().date()
            cursor.execute("""
                    SELECT * FROM ATTENDANCE 
                    WHERE user_id = %s AND attendance_date = %s
                """, (self.user_data['user_id'], today))

            if cursor.fetchone():
                messagebox.showinfo("Info", "Attendance already marked for today")
                return

        # Mark attendance
            cursor.execute("""
                    INSERT INTO ATTENDANCE 
                    (user_id, subscription_id, attendance_date, is_present)
                    VALUES (%s, %s, %s, TRUE)
                """, (self.user_data['user_id'], subscription['subscription_id'], today))

            conn.commit()
            messagebox.showinfo("Success", "Attendance marked successfully!")
            self.load_user_data()  # Refresh display

        except Exception as e:
            messagebox.showerror("Error", f"Failed to mark attendance: {str(e)}")
        finally:
            cursor.close()
            conn.close()


    def on_closing(self):
        """Handle window closing"""
        self.parent.destroy()  # Close the entire application


if __name__ == "__main__":
    # For testing purposes
    test_user = {'user_id': 1, 'username': 'test_user'}
    root = tk.Tk()
    root.withdraw()
    app = UserDashboard(root, test_user)
    root.mainloop()
