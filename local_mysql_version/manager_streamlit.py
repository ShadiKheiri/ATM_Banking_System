import streamlit as st
import pandas as pd
import datetime
from db_mysql import mydb
from backend import create_tables

st.title("Manager Dashboard")

# make sure database tables exist
if "db_init" not in st.session_state:
    create_tables()
    st.session_state["db_init"] = True

# state________________________________________________________________________
# check if filters exist in session state, if not initialize them
if "filters" not in st.session_state:
    st.session_state["filters"] = {
        "first_name": "",
        "last_name": "",
        "customer_id": "",
        "account": "",
        "city": "",
        "province": "",
        "postal": "",
        "phone": "",
        "email": "",
        "dob": None,}

if "filters_active" not in st.session_state:    # whether filters are applied
    st.session_state["filters_active"] = False  # default: not applied
if "reset_counter" not in st.session_state:     # to force new widgets on reset
    st.session_state["reset_counter"] = 0       # initial value

def reset_filters():
    f = st.session_state["filters"] 
    for k in f:                                 # reset each filter to default value
        f[k] = None if k == "dob" else ""       # 
    st.session_state["filters_active"] = False
    st.session_state["reset_counter"] += 1   # force new widgets

# data __________________________________________________________________________
# load customers with their account info
df_customers = pd.read_sql("""
    select
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
        c.email,
        a.account_number,
        a.balance
    from customer c
    left join account a on c.customer_id = a.customer_id
""", mydb)
# convert DOB to datetime
df_customers["DOB"] = pd.to_datetime(df_customers["DOB"], errors="coerce")

# sidebar ________________________________________________________________________
with st.sidebar:
    st.header("Filters")
    f = st.session_state["filters"] 
    rc = st.session_state["reset_counter"]

    # input widgets for each filter
    f["first_name"] = st.text_input("First name", f["first_name"], key=f"first_name_{rc}")
    f["last_name"] = st.text_input("Last name", f["last_name"], key=f"last_name_{rc}")
    f["customer_id"] = st.text_input("Customer ID", f["customer_id"], key=f"customer_id_{rc}")
    f["account"] = st.text_input("Account number", f["account"], key=f"account_{rc}")
    f["city"] = st.text_input("City", f["city"], key=f"city_{rc}")
    f["postal"] = st.text_input("Postal code", f["postal"], key=f"postal_{rc}")
    f["phone"] = st.text_input("Phone", f["phone"], key=f"phone_{rc}")
    f["email"] = st.text_input("Email", f["email"], key=f"email_{rc}")

    provinces = ["All", "Alberta", "British Columbia", "Manitoba", "New Brunswick",
                 "Newfoundland and Labrador", "Nova Scotia", "Ontario",
                 "Prince Edward Island", "Quebec", "Saskatchewan"]
    current = f["province"] or "All"
    sel = st.selectbox("Province", provinces,
                       index=provinces.index(current),
                       key=f"province_{rc}")
    f["province"] = "" if sel == "All" else sel

    dob_on = st.checkbox(
        "Filter by date of birth",
        value=f["dob"] is not None,
        key=f"dob_enabled_{rc}",)
    
    if dob_on:
        default_dob = f["dob"] or datetime.date(2000, 1, 1)
        f["dob"] = st.date_input(
            "Date of Birth",
            value=default_dob,
            min_value=datetime.date(1900, 1, 1),
            max_value=datetime.date.today(),
            key=f"dob_{rc}",)
    else:
        f["dob"] = None

    st.markdown("---")
    if st.button("Apply filters", key=f"apply_{rc}"):
        st.session_state["filters_active"] = True
    if st.button("Reset filters", key=f"reset_{rc}"):
        reset_filters()
        st.rerun()

filters = st.session_state["filters"]
active = st.session_state["filters_active"]

# tabs __________________________________________________________________________
tab1, tab2, tab3 = st.tabs(["Customers", "Accounts", "Transactions"])

with tab1: # customers' tab
    # apply filters to customers dataframe
    df = df_customers.copy()
    if active: # even partial matches are considered
        # na: False to avoid errors with NaN values
        if filters["first_name"]:
            df = df[df["first_name"].str.contains(filters["first_name"], case=False, na=False)]
        if filters["last_name"]:
            df = df[df["last_name"].str.contains(filters["last_name"], case=False, na=False)]
        if filters["customer_id"]:
            df = df[df["customer_id"].astype(str).str.contains(filters["customer_id"])]
        if filters["account"]:
            df = df[df["account_number"].astype(str).str.contains(filters["account"])]
        if filters["city"]:
            df = df[df["city"].str.contains(filters["city"], case=False, na=False)]
        if filters["province"]:
            df = df[df["province"].str.contains(filters["province"], case=False, na=False)]
        if filters["postal"]:
            df = df[df["postal_code"].str.contains(filters["postal"], case=False, na=False)]
        if filters["phone"]:
            df = df[df["phone"].astype(str).str.contains(filters["phone"])]
        if filters["email"]:
            df = df[df["email"].str.contains(filters["email"], case=False, na=False)]
        if filters["dob"]:
            df = df[df["DOB"].dt.date == filters["dob"]]
    df.index = df.index + 1  # start index from 1
    st.dataframe(df)

with tab2: # account's tab
    df = pd.read_sql(
        "select account_number, customer_id, pin, balance from account", mydb,)
    
    if active:
        if filters["customer_id"]:
            df = df[df["customer_id"].astype(str).str.contains(filters["customer_id"])]
        if filters["account"]:
            df = df[df["account_number"].astype(str).str.contains(filters["account"])]
    df.index = df.index + 1  # start index from 1
    st.dataframe(df)

with tab3: # transactions' tab
    df = pd.read_sql(
        'select transaction_id, account_number, type, amount, timestamp from transaction order by timestamp desc', mydb,)
    
    if active and filters["account"]:
        df = df[df["account_number"].astype(str).str.contains(filters["account"])]
    df.index = df.index + 1  # start index from 1
    st.dataframe(df)