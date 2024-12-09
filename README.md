# 450django - Backend API for React Frontend

This repository contains the backend Django application that serves as an API for the React frontend. The project uses SQLite as the database for local development. The following tutorial will guide you through setting up this project from scratch, both on Windows and macOS.

## Prerequisites

Before starting, you need to have some basic software installed on your computer. This tutorial assumes you're using a Windows or macOS computer.

### Software Required:

1. **Python** (Programming language used for the backend)
   - [Download Python](https://www.python.org/downloads/) (Ensure you have Python 3.8+ installed)

2. **Git** (To download the project from GitHub)
   - [Download Git](https://git-scm.com/downloads)

3. **Text Editor** (For viewing and editing files)
   - You can use any text editor, but we recommend [VSCode](https://code.visualstudio.com/) or [Notepad++](https://notepad-plus-plus.org/downloads/).

4. **Command Line Tools** (For running commands)
   - On **Windows**, use **Command Prompt** or **PowerShell**.
   - On **macOS**, use **Terminal**.

---

## Step-by-Step Guide

### Step 1: Install Python and Git

#### **Windows Instructions**

1. **Install Python**:
   - Download the installer from the [Python website](https://www.python.org/downloads/).
   - Run the installer and make sure to check the box that says **"Add Python to PATH"** during installation.
   - Once installed, confirm by opening **Command Prompt** or **PowerShell** and typing:
     ```bash
     python --version
     ```
     You should see the Python version number if it's installed correctly.

2. **Install Git**:
   - Download Git from [here](https://git-scm.com/downloads).
   - Run the installer and follow the installation steps.
   - Once installed, open **Command Prompt** or **PowerShell** and confirm by typing:
     ```bash
     git --version
     ```
     You should see the Git version number.

#### **macOS Instructions**

1. **Install Python**:
   - Download the installer from [Python's website](https://www.python.org/downloads/), or you can install it using **Homebrew** if you have it installed by running:
     ```bash
     brew install python
     ```
   - Verify installation by opening **Terminal** and typing:
     ```bash
     python3 --version
     ```
     You should see the Python version number.

2. **Install Git**:
   - Git is often pre-installed on macOS, but you can install it using **Homebrew**:
     ```bash
     brew install git
     ```
   - Confirm by typing:
     ```bash
     git --version
     ```
     You should see the Git version number.

---

### Step 2: Clone the Repository

Now that you have Git and Python set up, you'll need to download the project files.

1. Open **Command Prompt** or **PowerShell** (on Windows) or **Terminal** (on macOS), and navigate to the directory where you want to store your project files.
   
2. Run the following command to clone the repository from GitHub:
   ```bash
   git clone https://github.com/ethannussinov/450django.git
   ```
   This will create a folder named `450django` containing all the project files.

3. Navigate into the `450django` folder:
   ```bash
   cd 450django
   ```

---

### Step 3: Create a Virtual Environment

A virtual environment is like a separate workspace where you can install dependencies for your project without interfering with other projects.

#### **Windows Instructions**

1. In **Command Prompt** or **PowerShell**, create a virtual environment by running:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment by running:
   ```bash
   venv\Scripts\activate
   ```
   You should now see `(venv)` at the beginning of your command prompt, indicating that the virtual environment is active.

#### **macOS Instructions**

1. In **Terminal**, create a virtual environment by running:
   ```bash
   python3 -m venv venv
   ```

2. Activate the virtual environment by running:
   ```bash
   source venv/bin/activate
   ```
   You should now see `(venv)` at the beginning of your terminal prompt, indicating that the virtual environment is active.

---

### Step 4: Install Project Dependencies

1. With the virtual environment activated, install all the necessary libraries for the Django project:
   ```bash
   pip install -r requirements.txt
   ```

---

### Step 5: Set Up the Database

The project uses SQLite, a lightweight database that doesn't require any installation or setup.

1. Run the following command to set up the database:
   ```bash
   python manage.py migrate
   ```

   This command applies any necessary database changes (migrations) to get things ready.

---

### Step 6: Create a Superuser (Optional)

If you want to access the Django admin panel, you need to create a superuser account. We already created a superuser for you:\
(username: ethannussinov, password: engrlsem450)

1. Run the following command to create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

2. You will be prompted to enter a **username**, **email**, and **password**. Choose your own credentials.

---

### Step 7: Run the Django Server

Now that everything is set up, you can run the Django backend server locally.

1. Run the following command to start the server:
   ```bash
   python manage.py runserver 8080
   ```

   This will start the server on port 8080. You should see output similar to this:
   ```bash
   Starting development server at http://127.0.0.1:8080/
   ```
2. Open your web browser and visit:
    ```bash
    http://127.0.0.1:8080/admin
    ```
    
You should see a login page for administration.

---

### Step 8: Access the Django Admin Panel (Optional)

If you created a superuser, you can log into the Django admin panel to manage the project.

1. In your browser, go to:
    ```bash
    http://127.0.0.1:8080/admin/
    ```

2. Log in using the **username** and **password** you created earlier.

---

### Troubleshooting

- **Missing Dependencies**: If you see errors about missing packages, make sure you've installed everything with `pip install -r requirements.txt`.
- **Server Issues**: If you can’t access the server, ensure the server is running by checking the terminal output.

---

## Running the React Frontend

Once you’ve set up the backend, you can connect it from a [React frontend](https://github.com/ethannussinov/450react). Ensure the React app makes API requests to the Django server at `http://127.0.0.1:8080/`.
