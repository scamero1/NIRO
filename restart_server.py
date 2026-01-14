
import paramiko
import time

HOST = "157.173.110.101"
USER = "root"
PASS = "admindenequi12"

def restart_service():
    print(f"Connecting to {HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USER, password=PASS)
        
        print("Checking for running server...")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep server.py | grep -v grep")
        processes = stdout.read().decode().strip().split('\n')
        
        for p in processes:
            if p:
                parts = p.split()
                pid = parts[1]
                print(f"Killing process {pid}...")
                ssh.exec_command(f"kill -9 {pid}")
        
        print("Starting server...")
        # Start new server process
        # We need to make sure we are in the right directory
        cmd = "cd /root/NIRO && nohup python3 server.py > output.log 2>&1 &"
        ssh.exec_command(cmd)
        
        print("Server started in background.")
        
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    restart_service()
