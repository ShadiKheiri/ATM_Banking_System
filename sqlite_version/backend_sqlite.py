# import necessary libraries
import pandas as pd
from datetime import datetime
from db_SQLite import cursor, mydb
import regex
import os

# cursor is like remote control for interacting with the database
# cursor.execute: how you run SQL commands from python code
# create tables if not exist
def create_tables():

# create customer table to store customer info
    cursor.execute("""
    create table if not exists customer (
        customer_id integer primary key autoincrement,
        first_name text,
        last_name text,
        DOB text,
        app text,
        building text,
        street text,
        city text,
        province text,
        postal_code text,
        phone text,
        email text
    );
    """)

# create account table to store account info
    cursor.execute("""
    create table if not exists account (
        account_number integer primary key autoincrement,
        customer_id integer not null,
        pin text not null,
        balance real not null default 0,
        foreign key (customer_id) references customer(customer_id)
    )
    """)


# create transaction table to store transaction info
    cursor.execute("""
        create table if not exists "transaction" (
            transaction_id integer primary key autoincrement,
            account_number integer not null,
            type text not null,
            amount real not null,
            timestamp text default (datetime('now')),
            foreign key (account_number) references account(account_number)
        );
    """)


    mydb.commit()  # it saves all changes which had been made permanently
    print("Tables created or already exist.")

# validate all custoemr input before saving to database
def register_customer(first_name, last_name, dob, app, building, street, city, province, postal_code, phone, email, pin):
    errors = [] 
    name_pattern = r"^[\p{L}]+([ -][\p{L}]+)*$" # only letters without numbers or symbols

# first name
    if not regex.fullmatch(name_pattern, first_name):
        errors.append("Invalid first name.")

# last name
    if not regex.fullmatch(name_pattern, last_name):
        errors.append("Invalid last name.")

# DOB
    try:
        dob_date = datetime.strptime(dob, "%Y-%m-%d")
        if not (datetime(1900, 1, 1) <= dob_date <= datetime.now()): # between 1900 and now
            errors.append("Date of birth must be between 1900 and today.")
    except ValueError:
        errors.append("Invalid date of birth format (expected YYYY-MM-DD).")

# apartment number (optional)
    if app and not regex.fullmatch(r"^(\d+)(?:\s*([A-Za-z]))?$", app): # accepts format like 12, 12A, 12 A
        errors.append("Invalid apartment number format.")

# building number
    if not regex.fullmatch(r"^(\d+)(?:\s*([A-Za-z]))?$", building): # accepts format like 12, 12A, 12 A
        errors.append("Invalid building number format.")

# street
    if not regex.fullmatch(r"^[\p{L}\d\s.\-]+$", street): # letters, numbers, space, dot, hyphen
        errors.append("Invalid street name.")

# city
    if not regex.fullmatch(r"^[\p{L}\s\-]+$", city): # only letters, space, hyphens
        errors.append("Invalid city name.")

# province
    valid_provinces = [
        "Alberta", "British Columbia", "Manitoba", "New Brunswick", "Newfoundland and Labrador",
        "Nova Scotia", "Ontario", "Prince Edward Island", "Quebec", "Saskatchewan"
    ]
    if province not in valid_provinces:
        errors.append("Invalid province.")

# postal code
    if not regex.fullmatch(r"^[A-Z]\d[A-Z] \d[A-Z]\d$", postal_code): # must be in Canadian format
        errors.append("Invalid postal code format (e.g. A1B 2C3).")

# phone
    if phone and (not phone.isdigit() or len(phone) != 10): # must have exactly 10 digits
        errors.append("Phone number must be 10 digits.")

# email
    if email and (not regex.match(r"^[^@]+@[^@]+\.[^@]{2,}$", email) or len(email) < 6): 
        # at least one character before and after @ and 2 characters after final dot
        errors.append("Invalid email address.")

# PIN
    if not pin.isdigit() or len(pin) != 4: # must be exactly 4 digits
        errors.append("PIN must be exactly 4 digits.")

    # Raise all errors together if any
    if errors:
        raise ValueError(errors)


# cursor is like remote control for interacting with the database
# cursor.execute: how you run SQL commands from python code

# insert new customer record into the customer table
    cursor.execute("""
        insert into customer (first_name, last_name, dob, app, building, street, city, province, phone, email, postal_code)
        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (first_name.title(), last_name.title(), dob, app, building, street.title(), city.title(),
          province, phone, email, postal_code))
    
    mydb.commit()  # save customer row permanently
    customer_id = cursor.lastrowid  # id of the new customer

    # compute the next account number, starting from 10001
    cursor.execute("""
        select coalesce(max(account_number), 10000) + 1
        from account
    """)
    next_account_number = cursor.fetchone()[0]

    # create a new account for this customer with the given PIN and initial balance 100
    cursor.execute("""
        insert into account (account_number, customer_id, pin, balance)
        values (?, ?, ?, 100)
    """, (next_account_number, customer_id, pin))
    mydb.commit()  # save changes permanently

    return next_account_number  # returns a new account number that was just created in the account table


#this function returns all personal info for one account number by joining customer and account table
def view_personal_info(cursor, account_number):
    cursor.execute("""
        select c.first_name, c.last_name, c.DOB, c.app, c.building, c.street, c.city, c.province, c.postal_code, c.phone, c.email, a.account_number
        from customer c
        join account a on c.customer_id = a.customer_id
        where a.account_number = ? 
    """, (account_number,))
    # ? is a placeholder for the account number
    result = cursor.fetchone() # returns only the first matching row from the query
    
    if result:
        return {
            "First Name": result[0],
            "Last Name": result[1],
            "Date of Birth": result[2],
            "Address": ", ".join(part for part in result[3:9] if part),
            "Phone": result[9] if result[9] else "-",
            "Email": result[10] if result[10] else "-",
            "Account Number": result[11],
        }
    else: 
        return "No personal info found."


# Login existing customer
# check if account number and PIN match together
def login_customer(cursor, account, pin):
    cursor.execute("select * from account where account_number=? and pin=?", (account, pin))
    result = cursor.fetchone() # if credentials are correct, returns a row/ returns a tuple

    if result:
        return True, result[0] # account number from database
    else:
        return False, None

    
def update_customer_info(
    cursor,
    account_number,
    # these are the customer info which may be updated
    # first name, last name and DOB can't be updated by customer
    # if the customer doesn't enter a new value, the old value will be kept
    email=None, phone=None, app=None, building=None, street=None, city=None, province=None, postal_code=None
):

    cursor.execute("""
        select customer.customer_id,
               customer.app, customer.building, customer.street, customer.city, customer.province, customer.postal_code,
               customer.phone, customer.email
        from customer
        join account on customer.customer_id = account.customer_id
        where account.account_number = ?
    """, (account_number,)) # returns single-member tuple(instead of int)
    current = cursor.fetchone() # fetch current info

    if not current:
        return False  # no customer found

    # convert the tuple into readable variable names
    (customer_id, curr_app, curr_building, curr_street, curr_city, curr_province, curr_postal, curr_phone, curr_email
    ) = current

    # if None or empty string, keep the old values
    new_app = app.strip() if app else curr_app
    new_building = building.strip() if building else curr_building
    new_street = street.strip().title() if street else curr_street
    new_city = city.strip().title() if city else curr_city
    new_province = province.strip().title() if province else curr_province
    new_postal = postal_code.strip().upper() if postal_code else curr_postal
    new_email = email.strip() if email else curr_email
    new_phone = phone.strip() if phone else curr_phone

# validation patterns
    errors = []

# apartment
    if new_app and not regex.fullmatch(r"^(\d+)(?:\s*([A-Za-z]))?$", new_app): # accepts format like 12, 12A, 12 A
        errors.append("Invalid apartment number format (e.g., 123, 123A, 123 A).")

# building
    if new_building and not regex.fullmatch(r"^(\d+)(?:\s*([A-Za-z]))?$", new_building): # accepts format like 12, 12A, 12 A
        errors.append("Invalid building number format.")

# street
    if new_street and not regex.fullmatch(r"^[\p{L}\d\s.\-]+$", new_street): # letters, numbers, spaces, dot, hyphen
        errors.append("Invalid street name format.")

# city
    if new_city and not regex.fullmatch(r"^[\p{L}\s\-]+$", new_city): # only letters, space, hyphens
        errors.append("Invalid city name format.")

# province
    valid_provinces = [
        "Alberta", "British Columbia", "Manitoba", "New Brunswick", "Newfoundland and Labrador",
        "Nova Scotia", "Ontario", "Prince Edward Island", "Quebec", "Saskatchewan"
    ]
    if new_province and new_province not in valid_provinces:
        errors.append("Invalid province name.")

# postal code
    if new_postal and not regex.fullmatch(r"^[A-Z]\d[A-Z] \d[A-Z]\d$", new_postal): # must be in Canadian format
        errors.append("Invalid postal code format (e.g. A1B 2C3).")

# phone
    if new_phone and (not new_phone.isdigit() or len(new_phone) != 10): # must have exactly 10 digits
        errors.append("Phone number must be exactly 10 digits.")

# email
    if new_email and (not regex.match(r"^[^@]+@[^@]+\.[^@]{2,}$", new_email) or len(new_email) < 6):
         # at least one character before and after @ and 2 characters after final dot
        errors.append("Invalid email address.")

# stop if any validation fails
    if errors:
        raise ValueError(errors)

# update database if no errors
# # updates all fields, but keeps old values for any field the user leaves blank
# structure of the SQL
# using % safely inserts values into the querym keeps the code clean, prevents SQL injections
    cursor.execute("""
        update customer
        set app = ?, building = ?, street = ?, city = ?, province = ?, postal_code = ?, phone = ?, email = ?
        where customer_id = ?
    """, (new_app, new_building, new_street, new_city, new_province, new_postal, new_phone, new_email, customer_id))
    # fill the python placeholders
    mydb.commit() # save the changes

    return True

# change PIN
def change_pin(cursor, account_number, old_pin, new_pin):
    cursor.execute("select pin from account where account_number = ?", (account_number,)) # check if account exists
    result = cursor.fetchone() # get one row from select result

    if not result:  # Account not found
        return "Account not found."
    if result[0] != old_pin:  # Check if old PIN is correct
        return "Old PIN is incorrect."
    if not new_pin.isdigit() or len(new_pin) != 4:
        return "New PIN must be exactly 4 digits."

    cursor.execute("update account set pin = ? where account_number = ?", (new_pin, account_number))
    mydb.commit() # save the changes to the database
    return "PIN updated successfully."

def verify_forgot_pin_identity(cursor, account_number, first_name, last_name, dob):
    try:
        # verify the person asking for a new PIN
        cursor.execute("""
            select a.account_number
            from customer c
            join account a on c.customer_id = a.customer_id
            where a.account_number = ?
              and c.first_name = ?
              and c.last_name  = ?
              and c.DOB        = ?
        """, (account_number, first_name, last_name, dob))
        result = cursor.fetchone()
        if not result:
            return False, "No matching user found."
        return True, "Identity verified."
    except Exception as e:
        return False, f"Database error: {e}"


# forgot PIN
def forgot_pin(cursor, mydb, account_number, first_name, last_name, dob, new_pin):
    if not (isinstance(new_pin, str) and new_pin.isdigit() and len(new_pin) == 4):
        return False, "PIN must be exactly 4 digits."
    try:
        # verifies the person asking for a new PIN
        cursor.execute("""
            select a.account_number
            from customer c
            join account a on c.customer_id = a.customer_id
            where a.account_number = ? and c.first_name = ? and c.last_name = ? and c.DOB = ?
        """, (account_number, first_name, last_name, dob))
        result = cursor.fetchone()
        if not result:
            return False, "No matching user found."
        cursor.execute("update account set pin = ? where account_number = ?", (new_pin, account_number))
        mydb.commit() # makes it permanent
        return True, account_number
    except Exception as e:
        return False, "PIN reset failed."


# show account balance
def check_balance(cursor, account_number):
    cursor.execute("""
        select a.balance
        from account a
        where a.account_number = ?
    """, (account_number,))
    result = cursor.fetchone()  # Fetch the balance
    if result:
        return result[0]
    else:
        return None


def make_transaction(cursor, account_number, transaction_type, amount):
    if amount < 0.01:
        raise ValueError("Minimum amount is $0.01.")

    transaction_type = transaction_type.lower()
    # check balance if withdrawal
    if transaction_type == "withdrawal":
        cursor.execute("select balance from account where account_number = ?", (account_number,))
        balance = cursor.fetchone()
        if not balance:
            return "Account not found."
        if amount > balance[0]:
            raise ValueError("Insufficient funds.")
        cursor.execute("update account set balance = balance - ? where account_number = ?", (amount, account_number))

    elif transaction_type == "deposit":
        if amount > 10_000:
            raise ValueError("Deposit limit is $10,000.")
        else:
            cursor.execute("update account set balance = balance + ? where account_number = ?", (amount, account_number))

    else:
        raise ValueError("Invalid transaction type.")
    
    # record transaction
    cursor.execute("""
        insert into "transaction" (account_number, type, amount)
        values (?, ?, ?)
    """, (account_number, transaction_type, amount))

    mydb.commit() # saves changes to the database permanently
    return f"{transaction_type.capitalize()} successful."


# Show transaction history
def view_transactions(account_number):
    # uses the database connection directly and returns a DataFrame
    df = pd.read_sql("""
    select type, amount, timestamp
    from "transaction"
    where account_number = ?
    order by timestamp desc
    limit 10
    """, con=mydb, params=(account_number,))
    
    df.index += 1  # make index start at 1
    return df  # always return a DataFrame


# update CSV (with account_number starting at 10001)
def update_csv():
    script_dir = os.path.dirname(os.path.abspath(__file__)) # find the folder where the .py is located
    csv_path = os.path.join(script_dir, "customers.csv") # places the file into that folder
    try:
        # read customer data into a DataFrame
        df = pd.read_sql("""
            select 
                a.account_number,
                c.customer_id,
                c.first_name,
                c.last_name,
                c.DOB,
                c.app,
                c.building,
                c.street,
                c.city,
                c.province,
                c.postal_code,
                c.phone,
                c.email
            from customer c
            join account a on c.customer_id = a.customer_id
        """, con=mydb)

        # saves all customer and account data to customer.csv/ if index=True: it would contain an extra column 
        df.to_csv(csv_path, index=False) 
        print("CSV updated at:", csv_path)

    except PermissionError: # if the user has customers.csv open, it won't overwrite it and warns user to close the app(ex: excel)
        print("Cannot update CSV. Please close it in Excel and try again.")
    except Exception as e: # prevents getting any other errors
        print("Error updating CSV:", e)