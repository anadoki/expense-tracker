from datetime import datetime
import os
import platform
import re
import matplotlib
matplotlib.use('Agg')  # Force non-GUI backend for saving images
import matplotlib.pyplot as plt

common_categories = [
    "Food", "Transport", "Housing", "Entertainment",
    "Education", "Gas", "Groceries", "Dating", "Health",
    "Debt", "Rent", "Miscellaneous", "Clothing",
    "Utilities", "Insurance", "Savings", "Travel", "Subscriptions"
]

def validate_float(a):
     try:
          amount= round(float(a),2)
          return amount
     except (ValueError,TypeError):
          return False


def validate_date(date: str):

    if not isinstance(date, str): ##func to check if date is an instance of str
        return False

    date_formats = [
        "%m/%d/%Y",  # MM/DD/YYYY
        "%d/%m/%Y",  # DD/MM/YYYY
        "%Y-%m-%d",  # YYYY-MM-DD
    ]

    for date_format in date_formats: #for each format in list
            try:
                 parsed_date = datetime.strptime(date,date_format) #parsing date using strptime with input string w.r.t to each date format
                 return parsed_date.date().isoformat() #returning iso formatted date


            except ValueError:
                continue
    return False #if none matched

def validate_category(category: str) -> str:

    if category.title() in common_categories:
        return category.title()
    else:
        print(f"Warning: '{category}' is not a common category")
        return category.title().strip()

def view_cat_list():
     print("\n" + "="*65)
     print("AVAILABLE CATEGORIES".center(30))
     print("="*65)
     for i,cat in enumerate(common_categories,1):
          print(f"{i:>2}. {cat:<20}", end="")
          if i % 3 == 0:  # Three columns
            print()
     if len(common_categories) % 3 != 0:
          print()  # Ensure newline
     print("="*65)

def press_enter_to_continue():
    """Pause execution until user presses Enter"""
    input("\nPress Enter to return to menu...")
    # Optional: Clear screen after pause
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')


def print_menu():
    print("""
--- Expense Tracker Menu ---\n
1. Add Expense
2. Delete Expense
3. View Expenses
4. Update Expense
5. Summary
6. Plot Expenses by Category (Save Image)
7. Help
8. View Categories
9. Exit
""")

def help_desk():
    print("""
Help Desk:
- Enter only the number corresponding to your choice.
- Add Expense: Enter amount, category, description, and date.
- To cancel your choice, type 'q' when entering the first expense detail to go back to main menu.
- Date format should be YYYY-MM-DD.
- Delete Expense: Remove expense by ID.
- View Expenses: Lists all expenses with summary info.
- Update Expense: Modify existing expense by ID.
- Summary: Shows totals and category breakdown.
- Plot Expenses: Saves a bar chart of expenses by category.
- View Categories: Shows common categories for expenses.
- Exit: Closes the program.
""")



def format_currency(amount: float) -> str:
    """Format any number as $XX.XX """
    try:
         if amount is None:
              return "$0.00"
         return f"${abs(amount):,.2f}"

    except (ValueError,TypeError):
         return "$0.00"

def val_filename(filename: str):
     fpattern = r"^[^<>:\"/\\|?*\n\r$!%@{}#`+\=&]{1,18}\.[Pp][Nn][Gg]$"
     return bool(re.fullmatch(fpattern,filename))





