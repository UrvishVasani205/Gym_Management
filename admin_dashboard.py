import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from db_config import create_connection
from tkcalendar import DateEntry


class AdminDashboard:
    def __init__(self, parent, admin_data):
        self.parent = parent
        self.admin_data = admin_data

        # Create main window
        self.root = tk.Toplevel()
        self.root.title(f"Admin Dashboard - {admin_data['username']}")
        self.root.geometry("1200x800")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.create_widgets()
        self.load_initial_data()

    def create_widgets(self):
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)

        # Create tabs
        self.users_tab = ttk.Frame(self.notebook)
        self.payments_tab = ttk.Frame(self.notebook)
        self.stats_tab = ttk.Frame(self.notebook)
        self.classes_tab = ttk.Frame(self.notebook)  # New tab for managing classes

        self.notebook.add(self.users_tab, text='User Management')
        self.notebook.add(self.payments_tab, text='Payment History')
        self.notebook.add(self.stats_tab, text='Statistics')
        self.notebook.add(self.classes_tab, text='Manage Classes')  # Add Manage Classes tab

        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)

        # Setup each tab
        self.setup_users_tab()
        self.setup_payments_tab()
        self.setup_stats_tab()
        self.setup_classes_tab()  # Set up the new classes tab

    def setup_users_tab(self):
        # Filters Frame
        filters_frame = ttk.LabelFrame(self.users_tab, text="Filters", padding=10)
        filters_frame.pack(fill='x', padx=10, pady=5)

        # Date filters
        ttk.Label(filters_frame, text="Start Date:").grid(row=0, column=0, padx=5)
        self.start_date_filter = DateEntry(filters_frame, width=12)
        self.start_date_filter.grid(row=0, column=1, padx=5)

        ttk.Label(filters_frame, text="End Date:").grid(row=0, column=2, padx=5)
        self.end_date_filter = DateEntry(filters_frame, width=12)
        self.end_date_filter.grid(row=0, column=3, padx=5)

        # Status filter
        ttk.Label(filters_frame, text="Status:").grid(row=0, column=4, padx=5)
        self.status_filter = ttk.Combobox(filters_frame, values=['All', 'Active', 'Expired', 'Cancelled'])
        self.status_filter.set('All')
        self.status_filter.grid(row=0, column=5, padx=5)

        # Apply filters button
        ttk.Button(filters_frame, text="Apply Filters",
                   command=self.apply_filters).grid(row=0, column=6, padx=10)

        # Users Treeview
        self.users_tree = ttk.Treeview(self.users_tab,
                                       columns=('ID', 'Username', 'Email', 'Sub Status', 'Start Date', 'End Date',
                                                'Remaining Days'),
                                       show='headings')

        # Configure columns
        self.users_tree.heading('ID', text='ID')
        self.users_tree.heading('Username', text='Username')
        self.users_tree.heading('Email', text='Email')
        self.users_tree.heading('Sub Status', text='Subscription Status')
        self.users_tree.heading('Start Date', text='Start Date')
        self.users_tree.heading('End Date', text='End Date')
        self.users_tree.heading('Remaining Days', text='Remaining Days')

        # Set column widths
        self.users_tree.column('ID', width=50)
        self.users_tree.column('Username', width=100)
        self.users_tree.column('Email', width=200)
        self.users_tree.column('Sub Status', width=100)
        self.users_tree.column('Start Date', width=100)
        self.users_tree.column('End Date', width=100)
        self.users_tree.column('Remaining Days', width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.users_tab, orient='vertical',
                                  command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)

        # Pack elements
        self.users_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Bind double-click event
        self.users_tree.bind('<Double-1>', self.show_user_details)

    def setup_payments_tab(self):
        # Filters Frame
        filters_frame = ttk.LabelFrame(self.payments_tab, text="Payment Filters", padding=10)
        filters_frame.pack(fill='x', padx=10, pady=5)

        # Date range
        ttk.Label(filters_frame, text="From:").grid(row=0, column=0, padx=5)
        self.payment_start_date = DateEntry(filters_frame, width=12)
        self.payment_start_date.grid(row=0, column=1, padx=5)

        ttk.Label(filters_frame, text="To:").grid(row=0, column=2, padx=5)
        self.payment_end_date = DateEntry(filters_frame, width=12)
        self.payment_end_date.grid(row=0, column=3, padx=5)

        # Status filter
        ttk.Label(filters_frame, text="Status:").grid(row=0, column=4, padx=5)
        self.payment_status_filter = ttk.Combobox(filters_frame,
                                                  values=['All', 'Completed', 'Pending', 'Failed'])
        self.payment_status_filter.set('All')
        self.payment_status_filter.grid(row=0, column=5, padx=5)

        # Apply button
        ttk.Button(filters_frame, text="Apply Filters",
                   command=self.apply_payment_filters).grid(row=0, column=6, padx=10)

        ttk.Button(filters_frame, text="Refresh Payments",
                   command=self.load_payments_data).grid(row=0, column=7, padx=10)

        # Payments Treeview
        self.payments_tree = ttk.Treeview(self.payments_tab,
                                          columns=('ID', 'Username', 'Amount', 'Type', 'Status', 'Date'),
                                          show='headings')

        # Configure columns
        self.payments_tree = ttk.Treeview(self.payments_tab,
                                          columns=(
                                          'ID', 'Username', 'Amount', 'Type', 'Status', 'Date', 'Subscription Period'),
                                          show='headings')

        self.payments_tree.heading('ID', text='Transaction ID')
        self.payments_tree.heading('Username', text='Username')
        self.payments_tree.heading('Amount', text='Amount')
        self.payments_tree.heading('Type', text='Type')
        self.payments_tree.heading('Status', text='Status')
        self.payments_tree.heading('Date', text='Date')
        self.payments_tree.heading('Subscription Period', text='Subscription Period')  # New column

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.payments_tab, orient='vertical',
                                  command=self.payments_tree.yview)
        self.payments_tree.configure(yscrollcommand=scrollbar.set)

        # Pack elements
        self.payments_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')


    def load_users_data(self, filters=None):
        try:
            conn = create_connection()
            cursor = conn.cursor(dictionary=True)

            # Initialize params variable to an empty list, regardless of filters
            params = []

            query = """
                SELECT 
                    u.user_id,
                    u.username,
                    u.email,
                    s.status as sub_status,
                    s.start_date,
                    s.end_date,
                    s.remaining_days
                FROM USER u
                LEFT JOIN SUBSCRIPTION s ON u.user_id = s.user_id
                AND s.is_active = TRUE
            """

            if filters:
                conditions = []

                if filters.get('start_date'):
                    conditions.append("s.start_date >= %s")
                    params.append(filters['start_date'])

                if filters.get('end_date'):
                    conditions.append("s.end_date <= %s")
                    params.append(filters['end_date'])

                if filters.get('status') and filters['status'] != 'All':
                    conditions.append("s.status = %s")
                    params.append(filters['status'].lower())

                if conditions:
                    query += " WHERE " + " AND ".join(conditions)

            cursor.execute(query, tuple(params))  # Pass the params to the query
            users = cursor.fetchall()

            # Clear existing items in the Treeview
            self.users_tree.delete(*self.users_tree.get_children())

            # Insert new data into the Treeview
            for user in users:
                self.users_tree.insert('', 'end', values=(
                    user['user_id'],
                    user['username'],
                    user['email'],
                    user['sub_status'] or 'No subscription',
                    user['start_date'] or 'N/A',
                    user['end_date'] or 'N/A',
                    user['remaining_days'] or 'N/A'
                ))

            cursor.close()
            conn.close()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load users: {str(e)}")

    def load_payments_data(self, filters=None):
        try:
            conn = create_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT 
                    t.transaction_id,
                    u.username,
                    t.amount,
                    t.transaction_type,
                    t.status,
                    t.transaction_date,
                    s.start_date AS subscription_start,
                    s.end_date AS subscription_end
                FROM TRANSACTION t
                JOIN USER u ON t.user_id = u.user_id
                LEFT JOIN SUBSCRIPTION s ON t.subscription_id = s.subscription_id
            """

            # Initialize params to an empty list
            params = []

            # Add conditions based on filters
            if filters:
                conditions = []

                if filters.get('start_date'):
                    conditions.append("t.transaction_date >= %s")
                    params.append(filters['start_date'])

                if filters.get('end_date'):
                    conditions.append("t.transaction_date <= %s")
                    params.append(filters['end_date'])

                if filters.get('status') and filters['status'] != 'All':
                    conditions.append("t.status = %s")
                    params.append(filters['status'].lower())

                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY t.transaction_date DESC"

            # Execute query with parameters
            cursor.execute(query, tuple(params))
            payments = cursor.fetchall()

            # Update the payments tree view
            self.payments_tree.delete(*self.payments_tree.get_children())
            for record in payments:
                subscription_period = f"{record['subscription_start']} to {record['subscription_end']}" if record[ 'subscription_start'] and \
                                                                                                           record[ 'subscription_end'] else "N/A"
                self.payments_tree.insert('', 'end', values=(
                    record['transaction_id'],
                    record['username'],
                    f"{record['amount']:.2f}",
                    record['transaction_type'],
                    record['status'],
                    record['transaction_date'],
                    subscription_period  # New column value
                ))

            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load payments: {str(e)}")

    def load_statistics(self):
        try:
            conn = create_connection()
            cursor = conn.cursor(dictionary=True)

            # Revenue statistics
            cursor.execute("""
                SELECT 
                    SUM(amount) as total_revenue,
                    SUM(CASE WHEN transaction_date >= DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY) 
                        THEN amount ELSE 0 END) as monthly_revenue
                FROM TRANSACTION 
                WHERE status = 'completed'
            """)
            revenue_stats = cursor.fetchone()

            # User statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_users,
                    SUM(CASE WHEN EXISTS (
                        SELECT 1 FROM SUBSCRIPTION s 
                        WHERE s.user_id = u.user_id 
                        AND s.is_active = TRUE 
                        AND s.status = 'active'
                    ) THEN 1 ELSE 0 END) as active_users
                FROM USER u
            """)
            user_stats = cursor.fetchone()

            # Attendance statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as today_attendance,
                    (SELECT COUNT(*) / 30 
                     FROM ATTENDANCE 
                     WHERE attendance_date >= DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY)
                    ) as monthly_average
                FROM ATTENDANCE 
                WHERE attendance_date = CURRENT_DATE
            """)
            attendance_stats = cursor.fetchone()

            # Update labels
            self.total_revenue_label.config(
                text=f"Total Revenue: {revenue_stats['total_revenue']:.2f} units")
            self.monthly_revenue_label.config(
                text=f"Monthly Revenue: {revenue_stats['monthly_revenue']:.2f} units")

            self.total_users_label.config(
                text=f"Total Users: {user_stats['total_users']}")
            self.active_users_label.config(
                text=f"Active Users: {user_stats['active_users']}")

            self.today_attendance_label.config(
                text=f"Today's Attendance: {attendance_stats['today_attendance']}")
            self.monthly_attendance_label.config(
                text=f"Monthly Average Attendance: {attendance_stats['monthly_average']:.2f}")

            cursor.close()
            conn.close()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load statistics: {str(e)}")

    def setup_stats_tab(self):
        # Statistics Frames
        revenue_frame = ttk.LabelFrame(self.stats_tab, text="Revenue Statistics", padding=10)
        revenue_frame.pack(fill='x', padx=10, pady=5)

        self.total_revenue_label = ttk.Label(revenue_frame, text="Total Revenue: ")
        self.total_revenue_label.pack()

        self.monthly_revenue_label = ttk.Label(revenue_frame, text="Monthly Revenue: ")
        self.monthly_revenue_label.pack()

        # User Statistics
        user_frame = ttk.LabelFrame(self.stats_tab, text="User Statistics", padding=10)
        user_frame.pack(fill='x', padx=10, pady=5)

        self.total_users_label = ttk.Label(user_frame, text="Total Users: ")
        self.total_users_label.pack()

        self.active_users_label = ttk.Label(user_frame, text="Active Users: ")
        self.active_users_label.pack()

        # Attendance Statistics
        attendance_frame = ttk.LabelFrame(self.stats_tab, text="Attendance Statistics", padding=10)
        attendance_frame.pack(fill='x', padx=10, pady=5)

        self.today_attendance_label = ttk.Label(attendance_frame, text="Today's Attendance: ")
        self.today_attendance_label.pack()

        self.monthly_attendance_label = ttk.Label(attendance_frame, text="Monthly Average: ")
        self.monthly_attendance_label.pack()

    def setup_classes_tab(self):
        # Frame for adding new class
        add_class_frame = ttk.LabelFrame(self.classes_tab, text="Add New Class", padding=10)
        add_class_frame.pack(fill='x', padx=10, pady=5)

        # Class Name
        ttk.Label(add_class_frame, text="Class Name:").pack(anchor='w', pady=5)
        self.class_name_entry = ttk.Entry(add_class_frame, width=30)
        self.class_name_entry.pack(anchor='w')

        # Start Date
        ttk.Label(add_class_frame, text="Start Date:").pack(anchor='w', pady=5)
        self.class_start_date = DateEntry(add_class_frame, width=12)
        self.class_start_date.pack(anchor='w')

        # End Date
        ttk.Label(add_class_frame, text="End Date:").pack(anchor='w', pady=5)
        self.class_end_date = DateEntry(add_class_frame, width=12)
        self.class_end_date.pack(anchor='w')

        # Price
        ttk.Label(add_class_frame, text="Price:").pack(anchor='w', pady=5)
        self.class_price_entry = ttk.Entry(add_class_frame, width=30)
        self.class_price_entry.pack(anchor='w')

        # Add Class Button
        ttk.Button(add_class_frame, text="Add Class", command=self.add_class).pack(pady=10)

        # Classes Treeview (view added classes)
        self.classes_tree = ttk.Treeview(self.classes_tab,
                                         columns=('ID', 'Class Name', 'Start Date', 'End Date', 'Price'),
                                         show='headings')

        # Configure columns
        self.classes_tree.heading('ID', text='Class ID')
        self.classes_tree.heading('Class Name', text='Class Name')
        self.classes_tree.heading('Start Date', text='Start Date')
        self.classes_tree.heading('End Date', text='End Date')
        self.classes_tree.heading('Price', text='Price')

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.classes_tab, orient='vertical', command=self.classes_tree.yview)
        self.classes_tree.configure(yscrollcommand=scrollbar.set)

        # Pack elements
        self.classes_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Frame for managing enrolled users in classes
        enrolled_users_frame = ttk.LabelFrame(self.classes_tab, text="Users Enrolled in Classes", padding=10)
        enrolled_users_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Treeview for enrolled users
        self.enrolled_users_tree = ttk.Treeview(enrolled_users_frame,
                                                columns=('Username', 'Enrollment Date', 'Payment Status'),
                                                show='headings')
        self.enrolled_users_tree.heading('Username', text='Username')
        self.enrolled_users_tree.heading('Enrollment Date', text='Enrollment Date')
        self.enrolled_users_tree.heading('Payment Status', text='Payment Status')
        self.enrolled_users_tree.pack(fill='both', expand=True, padx=10, pady=5)

        # Class filter
        ttk.Label(enrolled_users_frame, text="Filter by Class:").pack(anchor='w', pady=5)
        self.class_filter_combobox = ttk.Combobox(enrolled_users_frame, postcommand=self.load_classes_filter, width=30)
        self.class_filter_combobox.pack(anchor='w', pady=5)

        # Button to apply the class filter
        ttk.Button(enrolled_users_frame, text="Filter", command=self.filter_enrolled_users).pack(pady=10)


    def load_initial_data(self):
        self.load_users_data()
        self.load_payments_data()
        self.load_statistics()
        self.load_classes_data()

    def load_classes_data(self):
        try:
            conn = create_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM CLASSES")  # Assuming CLASSES table exists
            classes = cursor.fetchall()

            # Clear existing items
            self.classes_tree.delete(*self.classes_tree.get_children())

            # Insert new data
            for class_data in classes:
                self.classes_tree.insert('', 'end', values=(
                    class_data['class_id'],
                    class_data['class_name'],
                    class_data['start_date'],
                    class_data['end_date'],
                    class_data['price']
                ))

            cursor.close()
            conn.close()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load classes: {str(e)}")

    def add_class(self, class_name, start_date, end_date, price):
        try:
            conn = create_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO CLASSES (class_name, start_date, end_date, price, is_active)
                VALUES (%s, %s, %s, %s, TRUE)
            """, (class_name, start_date, end_date, price))

            conn.commit()
            messagebox.showinfo("Success", "Class added successfully!")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to add class: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def filter_enrolled_users(self):
        selected_class = self.class_filter_combobox.get()
        if selected_class:
            class_id = self.get_class_id(selected_class)
            if class_id:
                self.load_enrolled_users(class_id)
        else:
            messagebox.showwarning("No Selection", "Please select a class to filter users.")

    def apply_filters(self):
        # Gather filters for users
        filters = {
            "start_date": self.start_date_filter.get_date() if self.start_date_filter.get() else None,
            "end_date": self.end_date_filter.get_date() if self.end_date_filter.get() else None,
            "status": self.status_filter.get() if self.status_filter.get() != "All" else None,
        }
        self.load_users_data(filters)

    def apply_payment_filters(self):
        # Gather filters for payments
        filters = {
            "start_date": self.payment_start_date.get_date() if self.payment_start_date.get() else None,
            "end_date": self.payment_end_date.get_date() if self.payment_end_date.get() else None,
            "status": self.payment_status_filter.get() if self.payment_status_filter.get() != "All" else None,
        }
        self.load_payments_data(filters)

    def show_user_details(self, event):
        # Get selected item
        selected_item = self.users_tree.selection()
        if selected_item:
            user_data = self.users_tree.item(selected_item, "values")
            messagebox.showinfo("User Details", f"Details for User ID: {user_data[0]}\n"
                                                f"Username: {user_data[1]}\n"
                                                f"Email: {user_data[2]}\n"
                                                f"Subscription Status: {user_data[3]}\n"
                                                f"Start Date: {user_data[4]}\n"
                                                f"End Date: {user_data[5]}\n"
                                                f"Remaining Days: {user_data[6]}")
        else:
            messagebox.showwarning("No Selection", "Please select a user to view details.")

    def load_classes_filter(self):
        try:
            conn = create_connection()
            cursor = conn.cursor(dictionary=True)

            # Fetch active classes for the filter dropdown
            cursor.execute("SELECT class_id, class_name FROM CLASSES WHERE is_active = TRUE")
            classes = cursor.fetchall()

            # Populate the combobox and ID mapping
            self.class_filter_combobox['values'] = [cls['class_name'] for cls in classes]
            self.class_id_mapping = {cls['class_name']: cls['class_id'] for cls in classes}

            # Close the cursor and connection
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load classes: {str(e)}")


    def load_enrolled_users(self, class_id):
        try:
            conn = create_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT u.username, e.enrollment_date, e.payment_status
                FROM ENROLLMENT e
                JOIN USER u ON e.user_id = u.user_id
            """
            params = []
            if class_id:
                query += " WHERE e.class_id = %s"
                params.append(class_id)

            cursor.execute(query, params)
            enrolled_users = cursor.fetchall()

        # Update the Treeview with enrolled users
            self.enrolled_users_tree.delete(*self.enrolled_users_tree.get_children())
            for record in enrolled_users:
                self.enrolled_users_tree.insert('', 'end', values=(
                    record['username'],
                    record['enrollment_date'],
                    record['payment_status']
                ))

            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load enrolled users: {str(e)}")

    def get_class_id(self, class_name):
        return self.class_id_mapping.get(class_name, None)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Are you sure you want to close the admin dashboard?"):
            self.root.destroy()
