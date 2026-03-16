import socket
import pymysql
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

password = os.getenv('MYSQL_PASSWORD', 'health@123')
results = []

def test_tcp(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect((host, port))
        s.close()
        return True, "TCP Open"
    except Exception as e:
        return False, str(e)

def test_conn(driver, host, port, user='root', pwd=''):
    try:
        if driver == 'pymysql':
            conn = pymysql.connect(host=host, port=port, user=user, password=pwd, connect_timeout=2)
        else:
            conn = mysql.connector.connect(host=host, port=port, user=user, password=pwd, connect_timeout=2, use_pure=True)
        conn.close()
        return True, "Success"
    except Exception as e:
        return False, str(e)

hosts = ['localhost', '127.0.0.1', '0.0.0.0', '192.168.1.17']
ports = [3306, 33060]

print(f"{'Host':<15} {'Port':<6} {'TCP':<10} {'PyMySQL':<30} {'MySQL-Connector':<30}")
print("-" * 100)

for h in hosts:
    for p in ports:
        tcp_ok, tcp_msg = test_tcp(h, p)
        py_ok, py_msg = test_conn('pymysql', h, p, pwd=password) if tcp_ok else (False, "N/A")
        my_ok, my_msg = test_conn('mysql.connector', h, p, pwd=password) if tcp_ok else (False, "N/A")
        
        print(f"{h:<15} {p:<6} {'OK' if tcp_ok else 'FAIL':<10} {py_msg[:30]:<30} {my_msg[:30]:<30}")
