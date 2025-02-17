import sqlite3
import pandas as pd

# Load CSV file into a DataFrame
csv_file_path = "/Users/surya/Downloads/employee_dataset.csv"  # Path to the uploaded file
df = pd.read_csv(csv_file_path)

# Print column names to verify structure
print("CSV Columns:", df.columns.tolist())

# Connect to SQLite database
connection = sqlite3.connect("employee1.db")
cursor = connection.cursor()

# Create table with all columns
# Corrected the table name from 'Employess_data' to 'Employee_data'
table_info = """
CREATE TABLE IF NOT EXISTS Employee_data (
    Education TEXT,
    CompanyName TEXT,
    JoiningYear INT,
    City TEXT,
    PaymentTier INT,
    Age INT,
    Gender TEXT,
    EverBenched TEXT,
    ExperienceInCurrentDomain INT,
    LeaveOrNot INT
);
"""
cursor.execute(table_info)

# Convert DataFrame to list of tuples for insertion
# Corrected the column name for experience from 'Experience' to 'ExperienceInCurrentDomain'
employees_data = df.itertuples(index=False, name=None)

# Insert records in bulk
cursor.executemany("INSERT INTO Employee_data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", employees_data)

# Display inserted records
print("Inserted records:")
data = cursor.execute("SELECT * FROM Employee_data LIMIT 1000")  # Fetch first 10 rows, not 1000
for row in data:
    print(row)

# Commit changes and close connection
connection.commit()
connection.close()