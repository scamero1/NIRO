
import paramiko
import os
import time
import sys

# Configuration
HOST = "157.173.110.101"
USER = "root"
PASS = "admindenequi12"
REMOTE_DIR = "/var/www/niro"
DOMAIN = "niro-tv.online"

# Mapping: Local File -> Remote File
FILE_MAPPING = {
    "index_pro.html": "index.html", # REVERT: Use index_pro.html as the main index
    "sw.js": "sw.js",
    "server.py": "server.py",
    "launcher.py": "launcher.py", 
    "app.js": "app.js",
    "styles.css": "styles.css",
    "requirements.txt": "requirements.txt",
    "manifest.json": "manifest.json",
    "Niro_original.png": "Niro_original.png"
}

def run_command(ssh, command):
    print(f"Running: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print(f"OUT: {out}")
    if err: print(f"ERR: {err}")
    return exit_status

def deploy():
    try:
        print(f"Connecting to {HOST}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=PASS)
        sftp = ssh.open_sftp()
        
        # Setup Directory
        run_command(ssh, f"mkdir -p {REMOTE_DIR}")
        
        # Upload Files
        print("Syncing files (FORCE OVERWRITE)...")
        for local_file, remote_file in FILE_MAPPING.items():
            if os.path.exists(local_file):
                local_size = os.path.getsize(local_file)
                remote_path = f"{REMOTE_DIR}/{remote_file}"
                
                print(f"Uploading {local_file} -> {remote_file} ({local_size} bytes)...")
                
                try:
                    sftp.remove(remote_path)
                except:
                    pass
                
                sftp.put(local_file, remote_path)
            else:
                print(f"WARNING: Local file {local_file} not found!")

        # Install Deps & Restart
        print("Installing Python dependencies...")
        run_command(ssh, f"cd {REMOTE_DIR} && pip3 install -r requirements.txt gunicorn --break-system-packages")
        
        print("Restarting Server...")
        # Kill existing python server
        run_command(ssh, "pkill -f server.py || true")
        # Start new one
        # Note: Using port 8001 as per previous config
        run_command(ssh, f"cd {REMOTE_DIR} && nohup python3 server.py > server.log 2>&1 &")
        
        print("Deployment Complete!")
        print(f"Visit: https://{DOMAIN}")
        
    except Exception as e:
        print(f"DEPLOYMENT FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    deploy()
