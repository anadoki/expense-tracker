from helpers import validate_float, validate_date, print_menu, help_desk, format_currency, view_cat_list, validate_category, press_enter_to_continue, val_filename
import matplotlib.pyplot as plt
import sqlite3
import shutil
import os
import platform
import subprocess
import matplotlib
matplotlib.use('Agg')

common_categories = [
    "Food", "Transport", "Housing", "Entertainment",
    "Education", "Gas", "Groceries", "Dating", "Health",
    "Debt", "Rent", "Miscellaneous", "Clothing",
    "Utilities", "Insurance", "Savings", "Travel", "Subscriptions"
]

label_map = {
    "id": "Expense ID",
    "amount": "Amount",
    "category": "Category",                    # for dynamic allocation for input and display
    "description": "Description",
    "date": "Date"
}


class UserCancelledException(Exception):
    pass


class DBManager:
    def __init__(self, dict_mode=False,db_path=None):
        self.dict_mode = dict_mode  # False=tuples, True=dictionaries

        if db_path:
            self.db_path = db_path
        else:
            home = os.path.expanduser("~") # get cross-platform home directory path
            db_dir = os.path.join(home, ".expense_tracker")
            os.makedirs(db_dir, exist_ok=True) # Create the directory if it doesn't exist
            self.db_path = os.path.join(db_dir, "expenses.db")  # Save the full path to the DB file

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)  # ← USE self.db_path

        if self.dict_mode:
            self.conn.row_factory = sqlite3.Row  # Dictionary access

        return self.conn.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.commit()
        self.conn.close()



def main():

    print(center_text(f"\n------- Welcome to the Expense Tracker! -------\n"))
    create_db()

    while True:

        print_menu()

        choice = input("\nEnter your choice (1-9): ").strip()
        print(f"User choice: {choice}\n")

        try:
            if choice == "1":
                add_expense()
            elif choice == "2":
                delete_expense()
            elif choice == "3":
                view_expenses()
            elif choice == "4":
                update_expense()
            elif choice == "5":
                summary()
            elif choice == "6":
                while True:
                    file_inp = input("Enter a file name (eg:'filename.png'): ").strip()
                    if val_filename(file_inp):
                        print("-"*70)
                        stats = sum_by_category()
                        plot_sums(stats, file_inp)
                        break
                    else:
                        print("Invalid filename! Try again.(Only PNG format/No special symbols)")

            elif choice == "7":
                help_desk()
            elif choice == "8":
                view_cat_list()
            elif choice == "9":
                print("\nThank you for using Expense Tracker! Goodbye!\n")
                break
            else:
                print("Invalid choice. Try again.")

            if choice in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                press_enter_to_continue()

        except EOFError:
            print("⚠️ Exited tracker abruptly.")
            press_enter_to_continue()
            return
        except UserCancelledException:
            print("Operation cancelled.")
            press_enter_to_continue()


        #except Exception as e:
            #print(f"Unexpected error: {e}")
            #press_enter_to_continue()



def create_db(db_path=None):
    with DBManager(db_path=db_path) as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            category TEXT,
            description TEXT,
            date TEXT
        )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_category ON expenses(category)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_date ON expenses(date)")


def add_expense(db_path=None):
    try:
        print("\n**** Add a New Expense! ****\n")

        while True:
            amount = input("Amount(or 'q' to cancel): ").strip()
            if amount.lower() == 'q':
                raise UserCancelledException
            val_amount = validate_float(amount)
            if val_amount is not False:
                break
            else:
                print("Invalid amount. Please enter a valid number.")

        while True:
            category = validate_category(input("Category: ").strip())
            if category in common_categories:
                break
            print(f"Invalid category. Choose from the list below.")
            view_cat_list()

        description = input("Description: ").strip()

        while True:
            date_input = input("Date (YYYY-MM-DD): ").strip()
            valid_date = validate_date(date_input)
            if valid_date:
                break
            print("Invalid date format. Try again.")

        insert_expense(val_amount, category, description, valid_date, db_path=db_path)

        print("*** Expense Added Successfully! ***\n")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except EOFError:
        print("\nInput terminated unexpectedly. Returning to main menu.")
        press_enter_to_continue()
        return

def insert_expense(amount, category, description, date, db_path=None):
    with DBManager(db_path=db_path) as cur:
        cur.execute("""
            INSERT INTO expenses (amount, category, description, date)
            VALUES (?, ?, ?, ?)
        """, (amount, category, description, date))

def get_all_expenses(db_path=None):
    with DBManager(dict_mode=True, db_path=db_path) as cur:
        cur.execute("SELECT id, amount, category, description, date FROM expenses")
        expenses = cur.fetchall()
    return expenses

def view_expenses(db_path=None):
    with DBManager(dict_mode=True) as cur:

        expenses = get_all_expenses(db_path=db_path)
        if not expenses:
            print("No expenses recorded")
            return  # Exit the function early
        print(f"\n{'EXPENSE OVERVIEW':^40}")
        print("-" * 70)
        for exp in expenses:
            print(
                f"ID: {exp['id']:<3} | "
                f"Date: {exp['date']:<10} | "
                f"Category: {exp['category']:<10} | "
                f"Amount: {format_currency(exp['amount']):<10}"
            )

            desc = exp['description'][:20] + ("..." if len(exp['description']) > 20 else "")
            print(f"\nDescription: {desc:>28}")
            print("-" * 70)

        while True:
            choice = input("\nView details? Enter ID (or 'm' for menu): ").strip().lower()

            if choice == 'm':
                break  # Exit the loop
            try:
                id_exp = int(choice)
                detail = next((e for e in expenses if e['id'] == id_exp), None)
                if detail:
                    print("=" * 40)
                    for key, value in dict(detail).items():
                        print(f"{label_map.get(key, key):<15}:{value}")

                    print("=" * 40)
                    break
                else:
                    print("Error: No expense with that ID")

            except ValueError:
                print("⚠️  Please enter numbers only")
            except sqlite3.Error:
                print(f"⚠️  No expense with ID {choice}")

def delete_expense_by_id(exp_id, db_path=None):
    with DBManager(db_path=db_path) as cur:
        cur.execute("SELECT id FROM expenses WHERE id=?", (exp_id,))
        if not cur.fetchone():
            return False  # ID not found
        cur.execute("DELETE FROM expenses WHERE id=?", (exp_id,))
    return True


def delete_expense(db_path=None):
    try:
        exp_id = int(input("Which expense would you like to delete?: ").strip())
        success = delete_expense_by_id(exp_id, db_path=db_path)
        if not success:
            print(f"Error: Expense ID {exp_id} doesn't exist")
        else:
            print(f"*** Expense {exp_id} deleted successfully ***")
    except ValueError:
        print("⚠️ Invalid input: Please enter a numeric ID")
    except sqlite3.Error as e:
        print(f"⚠️ Database error: {e}")

def get_expense_by_id(exp_id, db_path=None):
    with DBManager(dict_mode=True, db_path=db_path) as cur:
        cur.execute("SELECT * FROM expenses WHERE id=?", (exp_id,))
        return cur.fetchone()  # dict or None

def update_expense_by_id(exp_id, updated_data, db_path=None):
    with DBManager(db_path=db_path) as cur:
        cur.execute("""
            UPDATE expenses
            SET amount=?, category=?, description=?, date=?
            WHERE id=?
        """, (
            updated_data["amount"],
            updated_data["category"],
            updated_data["description"],
            updated_data["date"],
            exp_id
        ))


def update_expense(db_path=None):
    try:
        exp_id = input("Expense ID to be updated (Enter 'q' to cancel): ").strip()
        if exp_id.lower() == 'q':
            raise UserCancelledException
        exp_id = int(exp_id)

        expense = get_expense_by_id(exp_id, db_path=db_path)
        if not expense:
            print(f"\nError: No expense found with ID {exp_id}")
            return

        print("\n******* Current Expense Details *******\n")
        for key in expense.keys():
            print(f"{label_map.get(key):<15}: {expense[key]:<30}")

        print("\n******* Edit Now *******")
        updated = {}

        for key in expense.keys():
            if key == "id":
                continue

            new_val = input(f"{label_map.get(key)}: ").strip()
            if not new_val:
                updated[key] = expense[key]
                continue

            if key == "amount":
                while True:
                    validated = validate_float(new_val)
                    if validated is not False:
                        updated[key] = validated
                        break
                    else:
                        print("Invalid amount. Try again")
                        new_val = input(f"{label_map.get(key)}: ").strip()

            elif key == "date":
                while True:
                    validated = validate_date(new_val)
                    if validated:
                        updated[key] = validated
                        break
                    else:
                        print("Invalid date format! Try again. [YYYY-MM-DD]")
                        new_val = input(f"{label_map.get(key)}: ").strip()

            elif key == "category":
                while True:
                    validated = validate_category(new_val)
                    if validated in common_categories:
                        updated[key] = validated
                        break
                    else:
                        print(f"Invalid category. Choose from the list below.")
                        view_cat_list()
                        new_val = input(f"{label_map.get(key)}: ").strip()

            else:
                updated[key] = new_val

        update_expense_by_id(exp_id, updated, db_path=db_path)
        print(f"\n**** Expense {exp_id} updated successfully ****\n")

    except sqlite3.Error as e:
        print(f"⚠️ Database error: {e}")
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")
    except EOFError:
        print("\n⚠️ Input terminated unexpectedly. Returning to main menu.")
        press_enter_to_continue()



def summary():
    try:

        with DBManager() as cur:
            cur.execute("SELECT COUNT(*) FROM expenses")
            row_count = cur.fetchone()[0]
            if row_count == 0:
                print("NO EXPENSES RECORDED YET")
                return
            print(f"TOTAL NO. OF EXPENSES: {row_count}\n")

            cur.execute("SELECT SUM(amount) FROM expenses")
            total_amount = cur.fetchone()[0] or 0
            print(f"TOTAL AMOUNT SPENT: {format_currency(total_amount)}\n")

        cat_sum = sum_by_category()
        if cat_sum:
            print("CATEGORY BREAKDOWN")
            print("-" * 30)
            # Calculate padding for alignment
            max_len = max(len(cat[0]) for cat in cat_sum)
            cat_sum.sort(key=lambda x: x[1], reverse=True)

            for cat, amount in cat_sum:
                print(f"{cat.upper():<{max_len}} | {format_currency(amount):>10}")
            if total_amount > 0:
                print("-" * 30)
                for cat, amount in cat_sum:
                    pct = (amount/total_amount)*100
                    print(f"{cat.upper():<{max_len}} │ {pct:5.1f}% of total")

            print()

        single_expenses()
        date_range()
        max_category()
    except Exception as e:
        print(f"⚠️ Error in calc: {e}")


def sum_by_category():
    with DBManager() as cur:
        cur.execute("""
            SELECT category,
                   COALESCE(SUM(amount), 0) as total
            FROM expenses
            GROUP BY category
            HAVING total > 0
        """)  # Returns 0 instead of NULL # Only show categories with expenses
        return cur.fetchall()


def get_save_directory():
    system = platform.system()

    if system == "Windows":
        return os.path.expanduser("~\\Pictures")
    elif system == "Darwin":  # macOS
        return os.path.expanduser("~/Desktop")
    elif system == "Linux":
        return os.path.expanduser("~/Pictures")
    else:
        return os.getcwd()  # Default to current working directory


def plot_sums(data: tuple, filename: str):
    if not data or not filename:
        print("No data/filename required to plot.")
        return

    categories, total = zip(*data)

    # Determine where to save the image
    save_directory = get_save_directory()
    os.makedirs(save_directory, exist_ok=True)
    filename = os.path.join(save_directory, filename)

    if len(categories) > 6:
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.barh(categories, total, color='skyblue')
        ax.set_xlabel('Total Amount', fontweight='heavy')
        ax.set_ylabel('Category', fontweight='heavy')

    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(categories, total, color='skyblue')
        ax.set_xlabel('Category', fontweight='heavy', fontsize=12)
        ax.set_ylabel('Total Amount', fontweight='heavy', fontsize=12)
    ax.set_title('EXPENSE BREAKDOWN BY CATEGORY', fontsize=16, fontweight='bold', color='#142d8e')

    try:
        fig.savefig(filename)
        print(f"\n BAR GRAPH breaking down your expenses by category saved as {filename}!\n")
        print(f"Please check the saved image at: {os.path.abspath(filename)}\n")
    except Exception as e:
        print(f"Failed to save image: {e}")
        return  # or handle as needed

    try:
        # Attempt to open the image
        if platform.system() == "Windows":
            os.startfile(filename)
        elif platform.system() == "Darwin":  # macOS
            subprocess.call(["open", filename])
        elif platform.system() == "Linux" and os.environ.get("DISPLAY"):
            subprocess.call(["xdg-open", filename])
        else:
            print("Platform not recognized or no GUI available. Please open the image manually.")
        plt.close(fig)
    except Exception as e:
        print(f"⚠️ Failed to open image: {e}")
        # Fallback to current directory
        filename = "my_plot.png"
        fig.savefig(filename)
        plt.close(fig)
        print(f"Graph saved to current directory as {filename}")


def single_expenses():
    with DBManager() as cur:
        cur.execute("SELECT MIN(amount) FROM expenses")
        min_amount = cur.fetchone()[0]  # returns only first elem of tuple
        print(f"LOWEST SINGLE EXPENSE: {min_amount}\n")
        cur.execute("SELECT MAX(amount) FROM expenses")
        max_amount = cur.fetchone()[0]
        print(f"HIGHEST SINGLE EXPENSE: {max_amount}\n")


def date_range():
    with DBManager() as cur:
        cur.execute("SELECT MIN(date), MAX(date) FROM expenses")
        min_date, max_date = cur.fetchone()
        print(f"Date Range: {min_date} to {max_date}\n")


def max_category():
    with DBManager() as cur:
        cur.execute(
            "SELECT category, COUNT(*) as freq FROM expenses GROUP BY category ORDER BY freq DESC LIMIT 1")
        max = cur.fetchone()
    print("-- FREQUENTLY SPENT CATEGORY --\n")
    print(f"{max[0]}: {max[1]}")


def center_text(text):
    width = shutil.get_terminal_size(fallback=(80, 20)).columns
    return f"{text:^{width}}"


if __name__ == "__main__":
    main()
