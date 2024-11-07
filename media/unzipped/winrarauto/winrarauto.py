import subprocess
import os
import psycopg2

app_name = "Winrar"

def get_db_connection():
    conn = psycopg2.connect(
        dbname="app_database",
        user="postgres",
        password="admin",
        host="localhost",
        port="5432"
    )
    return conn

def install_winrar():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetching app details
    cursor.execute('SELECT * FROM apps WHERE name = %s', (app_name,))
    app = cursor.fetchone()
    
    if app is None:
        print("App not found in the database.")
        return
    
    # Assuming 'unzip_path' is at index 7, modify if necessary
    current_dir = app[7]
    
    print("WinRAR installing...")

    # Path to the setup.exe file
    setup_file = os.path.join(current_dir, 'winrar-x64-701.exe')

    # Command to run the setup file silently
    command = f'"{setup_file}" /S'

    # Run the command using subprocess
    subprocess.run(command, shell=True)
    print("WinRAR successfully installed.")

install_winrar()
