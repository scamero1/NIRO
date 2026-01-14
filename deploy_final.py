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
    "index_design.html",
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
        
        # 1. Install System Dependencies (Ensure environment is ready)
        print("Ensuring system dependencies...")
        run_command(ssh, "apt-get update -qq")
        run_command(ssh, "apt-get install -y git python3-pip python3-venv nginx certbot python3-certbot-nginx unzip")
        
        # 2. Setup Directory
        print("Setting up directory...")
        run_command(ssh, f"mkdir -p {REMOTE_DIR}")
        
        # 3. Sync Local Critical Files (Force Overwrite)
        print("Syncing latest local files (FORCE OVERWRITE)...")
        for file in FILES_TO_SYNC:
            if os.path.exists(file):
                local_size = os.path.getsize(file)
                remote_path = f"{REMOTE_DIR}/{file}"
                
                print(f"Uploading {file} ({local_size} bytes)...")
                
                # Delete remote file first to be sure
                try:
                    sftp.remove(remote_path)
                except:
                    pass # File might not exist
                
                sftp.put(file, remote_path)
                
                # Verify upload
                try:
                    remote_attr = sftp.stat(remote_path)
                    if remote_attr.st_size == local_size:
                        print(f" -> Verified: {file} OK")
                    else:
                        print(f" -> ERROR: Size mismatch for {file} (Remote: {remote_attr.st_size})")
                except Exception as e:
                    print(f" -> ERROR: Could not verify {file}: {e}")

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
    
    # Force no-cache for index.html and sw.js
    location = /index.html {{
        proxy_pass http://127.0.0.1:8001;
        add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0";
    }}
    
    location = /sw.js {{
        proxy_pass http://127.0.0.1:8001;
        add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0";
    }}

    location /media {{
        alias {REMOTE_DIR}/media;
        autoindex on;
    }}
}}
"""
        with open("nginx_conf_temp", "w") as f:
            f.write(nginx_conf)
            
        sftp.put("nginx_conf_temp", f"/etc/nginx/sites-available/{DOMAIN}")
        os.remove("nginx_conf_temp")
        
        run_command(ssh, f"ln -sf /etc/nginx/sites-available/{DOMAIN} /etc/nginx/sites-enabled/")
        run_command(ssh, "rm -f /etc/nginx/sites-enabled/default")
        run_command(ssh, "nginx -t")
        run_command(ssh, "systemctl restart nginx")
        
        # 7. SSL Setup (ignoring errors if already set)
        print("Setting up SSL with Certbot...")
        run_command(ssh, f"certbot --nginx -d {DOMAIN} --non-interactive --agree-tos -m admin@{DOMAIN} --redirect || echo 'Certbot failed or already set up'")

        # 8. Start Application
        print("Restarting Application...")
        run_command(ssh, "pkill gunicorn || true")
        time.sleep(2)
        # Ensure log file exists
        run_command(ssh, f"touch {REMOTE_DIR}/app.log")
        run_command(ssh, f"chmod 666 {REMOTE_DIR}/app.log")
        
        run_command(ssh, f"cd {REMOTE_DIR} && nohup gunicorn -w 4 -b 127.0.0.1:8001 server:app > app.log 2>&1 &")
        
        print("\n---------------------------------------------------")
        print("Deployment completed!")
        print(f"Web App: https://{DOMAIN}")
        print("---------------------------------------------------")
        
        sftp.close()
        ssh.close()
        
    except Exception as e:
        print(f"Deployment failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    deploy()