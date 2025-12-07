# ATM Banking System  
This project is a simple ATM and Manager Dashboard built with Python, Streamlit, and two types of databases: MySQL and SQLite.  
You can try it online or download it and run it on your computer.

## Live Demo (SQLite Version)
[You can test the app here](https://atm-banking-system.streamlit.app/)


## Features

### ATM User Features
- Create a new customer account  
- Login with account number and PIN  
- Recover your account using "Forgot PIN"  
- Check your balance  
- Deposit and withdraw money  
- See your past transactions  
- View and update your personal information  
- Change your PIN  
- Logout safely  

### Manager Dashboard
- View all customers, accounts, and transactions  
- Search and filter by name, city, province, date of birth, account number, and more  
- Personal details are partially hidden for privacy
  
---

## Project Overview

This project was built in two phases, each using a different database.

### Phase 1 — MySQL Version (Runs Locally Only)
The first version uses MySQL, which requires a database server.  
This version can only be used on your own computer.

Why MySQL?
- It is powerful and good for real world applications  
- Handles larger data  
- Great for practicing SQL and understanding database relationships  

This phase helped build the main logic of the banking system.

---

### Phase 2 — SQLite Version (Runs Locally and Online)
The second version uses SQLite, which stores data in a simple file.  
This version can run locally and can also be deployed online.

Live demo: https://atm-banking-system.streamlit.app/

Why SQLite?
- No setup needed, everything works instantly  
- Easy for anyone to download and run  
- Supported by Streamlit Cloud, so the app can go online  
- Perfect for sharing the project with others  

---

### Main Difference
- MySQL version: Needs a database server, good for learning and real systems  
- SQLite version: Lightweight, simple, easy to share, and works online  

By making two versions, the project shows how the same system can work with both a full database server and a lightweight database file.
