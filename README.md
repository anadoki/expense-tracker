# Expense Tracker
#### Video Demo:  [https://youtu.be/44wNdrhSmnQ?si=UVHiCmXncYC2vQdx](https://youtu.be/44wNdrhSmnQ?si=UVHiCmXncYC2vQdx)

#### Description:
- A simple CLI-based Python app to track your daily expenses, generate summaries, and save graphs.
- Add, update, and delete expenses
- View breakdowns by category
- Generate and save bar charts
- Works across Windows, macOS, and Linux


### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/anadoki/expense-tracker.git
   cd expense-tracker
   ```
2. (Optional but recommended) Create a virtual environment:
   ```bash
   python3 -m venv env
   source env/bin/activate  # For macOS/Linux
   OR
   .\env\Scripts\activate   # For Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app:
 ``` bash
 python project.py # or python3 if needed
 ```


### Menu Options

- Add new expense
- Delete expense by ID
- View all expenses
- Update existing expense
- View financial summary
- Generate expense category chart
- Help/instructions
- View available categories
- Exit program

## Data storage
Automatically creates database at:
- Linux/macOS - ~/.expense_tracker/expenses.db
- Windows - %USERPROFILE%\.expense_tracker\expenses.db

## Expense Management
- Add new expenses (amount, category, description, date)
- View all expenses (list or detailed view)
- Update existing records
- Delete expenses by ID

## Financial Insights
- Category breakdowns
- Highest/lowest single expenses
- Date range analysis
- Most frequent spending category

## Data Visualization
- Generate expense category bar charts
- Save as PNG images at common directory depending on OS else default to cwd
- Windows - "~\\Pictures"
- macOS - "~/Desktop"
- Linux - "~/Pictures"
- Auto-open generated charts

# Testing

```bash
 pytest test_project.py #to run test file
```
- Class TestExpTracker tests DB logic for all functionalities
- Regular test functions asserts helper functions (mostly validator and corrector functions)


# Contact
Anagha Nair - roseonice144@gmail.com





