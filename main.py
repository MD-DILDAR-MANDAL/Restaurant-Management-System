import tkinter as tk
from tkinter import messagebox
import mysql.connector
from datetime import datetime

def connect_to_database():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="dildar123",
        database="rms"
    )
    return connection

class RestaurantManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Restaurant Management System")
        
        # Light gray background
        self.root.configure(bg="#F5F5F5")  

        self.customer_name = tk.StringVar()
        self.customer_contact = tk.StringVar()
        self.items = {
            "Burger": 100,
            "Pizza": 200,
            "Pasta": 150,
            "Sandwich": 80,
            "Salad": 90
        }

        self.orders = {}
        self.gst_percentage = 10  # GST percentage

        self.create_gui()

    def create_gui(self):
        # Customer details frame
        details_frame = tk.LabelFrame(self.root, text="Customer Details", bg="#FFFFFF", fg="#333333", font=("Helvetica", 12))
        details_frame.pack(fill="x", padx=10, pady=10)

        # Customer name label and entry
        name_label = tk.Label(details_frame, text="Name:", bg="#FFFFFF", fg="#333333", font=("Helvetica", 10))
        name_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        name_entry = tk.Entry(details_frame, textvariable=self.customer_name, font=("Helvetica", 10))
        name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Customer contact label and entry
        contact_label = tk.Label(details_frame, text="Contact:", bg="#FFFFFF", fg="#333333", font=("Helvetica", 10))
        contact_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        contact_entry = tk.Entry(details_frame, textvariable=self.customer_contact, font=("Helvetica", 10))
        contact_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Menu frame
        menu_frame = tk.LabelFrame(self.root, text="Menu", bg="#FFFFFF", fg="#333333", font=("Helvetica", 12))
        menu_frame.pack(fill="both", expand=True, padx=10, pady=10)

        row = 1
        for item, price in self.items.items():
            quantity_var = tk.IntVar()
            item_label = tk.Label(menu_frame, text=f"{item} - ₹{price}", bg="#FFFFFF", fg="#333333", font=("Helvetica", 10))
            item_label.grid(row=row, column=0, padx=5, pady=5, sticky="w")

            quantity_entry = tk.Entry(menu_frame, width=5, textvariable=quantity_var, font=("Helvetica", 10))
            quantity_entry.grid(row=row, column=1, padx=5, pady=5)

            self.orders[item] = {"quantity_var": quantity_var, "price": price}

            row += 1

        # Button frame
        button_frame = tk.Frame(self.root, bg="#F5F5F5")
        button_frame.pack(fill="x", padx=10, pady=10)

        # Print bill button
        print_bill_button = tk.Button(button_frame, text="Print Bill", bg="#4CAF50", fg="#FFFFFF", font=("Helvetica", 10), command=self.print_bill)
        print_bill_button.pack(side="left", padx=5)

        # Past records button
        past_records_button = tk.Button(button_frame, text="Past Records", bg="#03A9F4", fg="#FFFFFF", font=("Helvetica", 10), command=self.past_records)
        past_records_button.pack(side="left", padx=5)

        # Search record button
        search_record_button = tk.Button(button_frame, text="Search Record", bg="#FF9800", fg="#FFFFFF", font=("Helvetica", 10), command=self.search_record)
        search_record_button.pack(side="left", padx=5)

        # Sample bill text
        self.sample_bill_text = tk.Text(self.root, height=10, bg="#FFFFFF", fg="#333333", font=("Helvetica", 10))
        self.sample_bill_text.pack(fill="x", padx=10, pady=10)

    def print_bill(self):
        # Validate customer details
        if not self.customer_name.get().strip():
            messagebox.showwarning("Warning", "Please enter customer name.")
            return

        if not self.customer_contact.get().strip():
            messagebox.showwarning("Warning", "Please enter customer contact.")
            return

        selected_items = []
        total_price = 0
        num_items = 0

        # Collect selected items and calculate total price and quantity
        for item, info in self.orders.items():
            quantity = info["quantity_var"].get()
            if quantity:
                selected_items.append((item, quantity))
                total_price += quantity * info["price"]
                num_items += quantity

        if not selected_items:
            messagebox.showwarning("Warning", "Please select at least one item.")
            return

        # Calculate GST and grand total
        gst_amount = (total_price * self.gst_percentage) / 100
        grand_total = total_price + gst_amount

        # Save bill to database
        connection = connect_to_database()
        cursor = connection.cursor()

        # Save customer details and total prices to the `bills` table
        cursor.execute(
            "INSERT INTO bills (customer_name, customer_contact, total_price, gst_amount, grand_total) VALUES (%s, %s, %s, %s, %s)",
            (self.customer_name.get(), self.customer_contact.get(), total_price, gst_amount, grand_total)
        )

        # Get the ID of the newly inserted bill
        bill_id = cursor.lastrowid

        # Save items to the `items` table
        for item, quantity in selected_items:
            cursor.execute(
                "INSERT INTO items (bill_id, item_name, quantity, item_price) VALUES (%s, %s, %s, %s)",
                (bill_id, item, quantity, self.orders[item]["price"])
            )

        # Commit the transaction
        connection.commit()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Display bill in a message box
        bill = f"Customer Name: {self.customer_name.get()}\n"
        bill += f"Customer Contact: {self.customer_contact.get()}\n\n"
        bill += "Selected Items:\n"
        for item, quantity in selected_items:
            bill += f"{item} x {quantity}\n"
        bill += f"\nTotal Price: ₹{total_price}\n"
        bill += f"GST ({self.gst_percentage}%): ₹{gst_amount}\n"
        bill += f"Grand Total: ₹{grand_total}"

        messagebox.showinfo("Bill", bill)

        # Update sample bill text
        self.sample_bill_text.delete("1.0", tk.END)
        self.sample_bill_text.insert(tk.END, bill)

        # Clear inputs
        self.clear_inputs()

    def past_records(self):
        """Display past records in a message box."""
        connection = connect_to_database()
        cursor = connection.cursor()

        # Fetch all bills
        cursor.execute("SELECT * FROM bills")
        bills = cursor.fetchall()

        # Display records in a readable format
        past_records = []
        for bill in bills:
            bill_id, customer_name, customer_contact, total_price, gst_amount, grand_total, bill_date = bill
            past_records.append(
                f"Bill ID: {bill_id}\n"
                f"Customer Name: {customer_name}\n"
                f"Customer Contact: {customer_contact}\n"
                f"Date: {bill_date}\n"
                f"Total Price: ₹{total_price}\n"
                f"GST Amount: ₹{gst_amount}\n"
                f"Grand Total: ₹{grand_total}\n\n"
            )

        messagebox.showinfo("Past Records", "".join(past_records))

        cursor.close()
        connection.close()

    def search_record(self):
        """Search records by customer name."""
        search_window = tk.Toplevel(self.root)
        search_window.title("Search Record")

        # Search input
        search_name = tk.StringVar()
        tk.Label(search_window, text="Enter Customer Name:").pack(pady=5)
        search_entry = tk.Entry(search_window, textvariable=search_name)
        search_entry.pack(pady=5)
        search_button = tk.Button(search_window, text="Search", command=lambda: self.fetch_record(search_name.get(), search_window))
        search_button.pack(pady=5)

    def fetch_record(self, name, window):
        """Fetch and display record by customer name."""
        connection = connect_to_database()
        cursor = connection.cursor()

        # Search the bills table for the given customer name
        cursor.execute("SELECT * FROM bills WHERE customer_name = %s", (name,))
        bills = cursor.fetchall()

        # Display records in a readable format
        if not bills:
            messagebox.showinfo("Search Result", "No records found for the specified customer name.")
        else:
            search_result = []
            for bill in bills:
                bill_id, customer_name, customer_contact, total_price, gst_amount, grand_total, bill_date = bill
                search_result.append(
                    f"Bill ID: {bill_id}\n"
                    f"Customer Name: {customer_name}\n"
                    f"Customer Contact: {customer_contact}\n"
                    f"Date: {bill_date}\n"
                    f"Total Price: ₹{total_price}\n"
                    f"GST Amount: ₹{gst_amount}\n"
                    f"Grand Total: ₹{grand_total}\n\n"
                )

                # Fetch the items associated with the bill
                cursor.execute("SELECT * FROM items WHERE bill_id = %s", (bill_id,))
                items = cursor.fetchall()
                search_result.append("Items:\n")
                for item in items:
                    _, _, item_name, quantity, item_price = item
                    search_result.append(f"{item_name} x {quantity}\n")

            messagebox.showinfo("Search Result", "".join(search_result))

        cursor.close()
        connection.close()
        window.destroy()

    def clear_inputs(self):
        """Clear all input fields."""
        self.customer_name.set("")
        self.customer_contact.set("")
        for item, info in self.orders.items():
            info["quantity_var"].set(0)

if __name__ == "__main__":
    root = tk.Tk()
    rms = RestaurantManagementSystem(root)
    root.mainloop()
