import paramiko
import sys

# Configuration
HOST = "157.173.110.101"
USER = "root"
PASS = "admindenequi12"

def check_logs():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=PASS)
        
        print("Checking app.log...")
        stdin, stdout, stderr = ssh.exec_command("cat /var/www/niro/app.log")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_logs()
