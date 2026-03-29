"""
Author: Leticia Rodrigues
Assignment: #2
Description: Port Scanner — A tool that scans a target machine for open network ports
"""

# Import the required modules (Step ii)
# socket, threading, sqlite3, os, platform, datetime
import socket
import threading
import sqlite3
import os
import platform
import datetime

#  Print Python version and OS name (Step iii)
print("Python Version:", platform.python_version())
print("Operating System:", os.name)

common_ports = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    8080: "HTTP-Alt"
}

class NetworkTool:
    def __init__(self, target):
        self.__target = target

    @property
    def target(self):
            return self.__target
        
    @target.setter
    def target(self, value):
        if value == "":
            print("Error: Target cannot be empty")
        else:
            self.__target = value

    def __del__(self):
        print("NetworkTool instance destroyed")

            
# Q3: What is the benefit of using @property and @target.setter?

# Using @property allows controlled acess to private variables.
# The setter ensures that invalid values, such as an empty strings are not assigned.
# This improves data validation and protects the internal state of the object.


# Q1: How does PortScanner reuse code from NetworkTool?

# PortScanner inherits from NetworkTool, which allows it to reuse the target property and validation logic.
# For example, it uses the parent constructor through super().init(target) instead of redefining how the target is stored.

class PortScanner(NetworkTool):
    def __init__(self, target):
        super().__init__(target)
        self.scan_results = []
        self.lock = threading.Lock()

    def __del__(self):
        print("PortScanner intance destroyed")
        super().__del__()



#     Q4: What would happen without try-except here?

#     Without try-excepted, the program could crash if a connect error occurs.
#     For example, if the target is unreachable, the socket operation would raise an exception.
#     The try-except block ensures the program continues running even when errors happen.

# - scan_port(self, port):
    def scan_port(self, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)

            result = sock.connect_ex((self.target, port))

            if result == 0:
                status = "Open"
            else:
                 status = "Closed"

            service = common_ports.get(port, "Unknown")

            self.lock.acquire()
            self.scan_results.append((port, status, service))
            self.lock.release()

        except socket.error as e:
            print(f"Error scanning port {port}: {e}")

        finally:
            sock.close()


#
# - get_open_ports(self):

    def get_open_ports(self):
        open_ports = []

        for r in self.scan_results:
            if r[1] == "Open":
                open_ports.append(r)

        return open_ports
#
#     Q2: Why do we use threading instead of scanning one port at a time?
#     Threading allows multiple port to be snned at the same time,  which makes the program much faster.
#     Without threading, scanning 1024 ports would take a long time because each port would be checked sequentially.
#     Using threads improves effiency by running many checks at the same time.

# - scan_range(self, start_port, end_port):

    def scan_range(self, start_port, end_port):
        threads = []

        for port in range(start_port, end_port+1):
            t = threading.Thread(target=self.scan_port, args=(port,))
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()



def save_results(target, results):
        try:
            conn = sqlite3.connect("scan_history.db")
            cursor = conn.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT,
                port INTEGER,
                status TEXT,
                service TEXT,
                scan_date TEXT     
            )
            """)

            for port, status, service in results:
                cursor.execute(
                    "INSERT INTO scans (target, port, status, service, scan_date) VALUES (?, ?, ?, ?, ?)",
                    (target, port, status, service, str(datetime.datetime.now()))
                )

            conn.commit()
            conn.close()

        except sqlite3.Error as e:
            print("Database error:", e)
    

def load_past_scans():
        try:
            conn = sqlite3.connect("scan_history.db")
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM scans")
            rows = cursor.fetchall()

            for row in rows:
                print(f"[{row[5]}] {row[1]}: Port {row[2]} ({row[4]}) - {row[3]}")

            conn.close()

        except: 
            print("No past scan found.")


# ============================================================
# MAIN PROGRAM
# ============================================================
if __name__ == "__main__":
    try:
        target = input ("Enter target IP (default 127.0.0.1): ") or "127.0.0.1"

        start_port = int(input("Start port (1-1024): "))
        end_port = int(input("End port (1-1024): "))

        if start_port < 1 or end_port > 1024:
            print("Port must be between 1 and 1024")
            exit()

    except ValueError:
        print("Invalid input. Enter a valid Integer")
        exit()


    scanner = PortScanner(target)
    print(f"Scanning {target} from port {start_port} to {end_port}...")

    scanner.scan_range(start_port, end_port)

    open_ports = scanner.get_open_ports()

    print("\n ---- Scan results ----")
    for port, status, service in open_ports:
        print(f"Port {port}: {status} ({service})")


    print(f"Total open ports found: {len(open_ports)}")

    save_results(target, scanner.scan_results)

    choice = input("Would you like to see past scan history? (yes/no): ")

    if choice.lower() == "yes":
        load_past_scans()

# Q5: New Feature Proposal
# I would add a feature that allows the user to filter scan results by specifc service,
# such as HTTP or SSH. After scanning, the user could enter a service name and the program would display only the matching ports.
#  This could be implemented using a list comprehension to filter the scan_results list based on the service name.
#  # Diagram: See diagram_studentID.png in the repository root
