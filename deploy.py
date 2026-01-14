import paramiko
import os
import time
import sys

# Configuration
HOST = "157.173.110.101"
USER = "root"
PASS = "admindenequi12"
REMOTE_DIR = "/var/www/niro"
REPO_URL = "https://github.com/scamero1/NIRO.git"
DOMAIN = "niro-tv.online"

# Files to sync from local to remote to ensure latest version overrides git
FILES_TO_SYNC = [
    "index.html",
    "index_v3.html",
    "sw.js",
    "server.py",
    "launcher.py", 
    "app.js",
    "styles.css",
    "requirements.txt"
]

def run_command(ssh, command):
    print(f"Running: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    # Wait for command to finish
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
        
        # 1. Install System Dependencies
        print("Installing system dependencies...")
        run_command(ssh, "apt-get update")
        run_command(ssh, "apt-get install -y git python3-pip python3-venv nginx certbot python3-certbot-nginx unzip")
        
        # 2. Setup Directory & Git Clone
        print("Setting up directory and cloning repo...")
        # Check if dir exists
        check = run_command(ssh, f"test -d {REMOTE_DIR} && echo exists")
        if check == 0:
            print("Directory exists, pulling latest changes...")
            run_command(ssh, f"cd {REMOTE_DIR} && git reset --hard && git pull")
        else:
            print("Cloning repository...")
            run_command(ssh, f"git clone {REPO_URL} {REMOTE_DIR}")
        
        # 3. Sync Local Critical Files (Overriding Git)
        print("Syncing latest local files to ensure consistency...")
        for file in FILES_TO_SYNC:
            if os.path.exists(file):
                print(f"Uploading {file}...")
                sftp.put(file, f"{REMOTE_DIR}/{file}")
        
        # 4. Upload Pre-compiled EXE
        # print("Uploading NIRO_App.exe...")
        # run_command(ssh, f"mkdir -p {REMOTE_DIR}/media")
        # if os.path.exists("dist/NIRO_App.exe"):
        #     try:
        #         sftp.put("dist/NIRO_App.exe", f"{REMOTE_DIR}/media/NIRO_App.exe")
        #     except Exception as e:
        #         print(f"Error uploading EXE: {e}")
        # else:
        #     print("WARNING: dist/NIRO_App.exe not found locally. Skipping EXE upload.")

        # 5. Python Setup
        print("Installing Python dependencies...")
        run_command(ssh, f"cd {REMOTE_DIR} && pip3 install -r requirements.txt gunicorn --break-system-packages")
        
        # 6. Nginx Configuration
        print("Configuring Nginx...")
        nginx_conf = f"""
server {{
    listen 80;
    server_name {DOMAIN} www.{DOMAIN};
    client_max_body_size 100M;

    location / {{
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
        with open("niro_nginx", "w") as f:
            f.write(nginx_conf)
        
        sftp.put("niro_nginx", f"/etc/nginx/sites-available/{DOMAIN}")
        run_command(ssh, f"ln -sf /etc/nginx/sites-available/{DOMAIN} /etc/nginx/sites-enabled/")
        run_command(ssh, "rm -f /etc/nginx/sites-enabled/default")
        run_command(ssh, "nginx -t")
        run_command(ssh, "systemctl restart nginx")
        
        # 7. SSL Setup (Certbot)
        print("Setting up SSL with Certbot...")
        # We use --register-unsafely-without-email to avoid prompts if not already registered
        run_command(ssh, f"certbot --nginx -d {DOMAIN} --non-interactive --agree-tos -m admin@{DOMAIN} --redirect || echo 'Certbot failed or already set up'")
        
        # 8. Start Application
        print("Starting Application...")
        run_command(ssh, "pkill gunicorn || true")
        # Run in background
        run_command(ssh, f"cd {REMOTE_DIR} && nohup gunicorn -w 4 -b 127.0.0.1:8001 server:app > app.log 2>&1 &")
        
        print("\n---------------------------------------------------")
        print("Deployment completed!")
        print(f"Web App: https://{DOMAIN}")
        print(f"Download EXE: https://{DOMAIN}/media/NIRO_App.exe")
        print("---------------------------------------------------")
        
    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        if 'ssh' in locals(): ssh.close()
        if os.path.exists("niro_nginx"): os.remove("niro_nginx")

if __name__ == "__main__":
    deploy()
