import paramiko
import os
import zipfile
import time
import sys

# Configuration
HOST = "157.173.110.101"
USER = "root"
PASS = "admindenequi12"
REMOTE_DIR = "/var/www/niro"
DOMAIN = "niro-tv.online"

def create_zip(zip_name):
    print(f"Creating {zip_name}...")
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('.'):
            # Ignore hidden folders and venv and dist
            if '.venv' in root or '.git' in root or '__pycache__' in root or 'dist' in root or 'build' in root:
                continue
            
            for file in files:
                if file == zip_name or file.endswith('.pyc') or file.endswith('.exe'):
                    continue
                
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, '.')
                zipf.write(file_path, arcname)
    print("Zip created.")

def run_command(ssh, command, sudo=True):
    if sudo and USER != 'root':
        command = f"echo {PASS} | sudo -S {command}"
    
    print(f"Running: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    
    if out: print(f"OUT: {out}")
    if err: print(f"ERR: {err}")
    
    return exit_status

def deploy():
    zip_name = "niro_deploy.zip"
    create_zip(zip_name)
    
    try:
        print(f"Connecting to {HOST}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=PASS)
        
        sftp = ssh.open_sftp()
        
        # 1. Install dependencies
        print("Installing system dependencies...")
        # Check if apt is locked, wait if needed
        run_command(ssh, "while fuser /var/lib/dpkg/lock >/dev/null 2>&1; do sleep 1; done")
        run_command(ssh, "apt-get update")
        run_command(ssh, "apt-get install -y python3-pip python3-venv nginx certbot python3-certbot-nginx unzip")
        
        # 2. Setup directory
        print("Setting up directory...")
        run_command(ssh, f"mkdir -p {REMOTE_DIR}")
        run_command(ssh, f"chown -R {USER}:{USER} {REMOTE_DIR}")
        
        # 3. Upload file
        print("Uploading files...")
        sftp.put(zip_name, f"/tmp/{zip_name}")
        run_command(ssh, f"mv /tmp/{zip_name} {REMOTE_DIR}/{zip_name}")
        
        # Upload EXE if exists
        if os.path.exists("dist/NIRO_App.exe"):
            print("Uploading NIRO_App.exe...")
            run_command(ssh, f"mkdir -p {REMOTE_DIR}/media")
            sftp.put("dist/NIRO_App.exe", f"{REMOTE_DIR}/media/NIRO_App.exe")
        
        # 4. Unzip and Install Python reqs
        print("Installing Python dependencies...")
        run_command(ssh, f"cd {REMOTE_DIR} && unzip -o {zip_name}")
        run_command(ssh, f"cd {REMOTE_DIR} && pip3 install -r requirements.txt gunicorn --break-system-packages")
        
        # 5. Configure Nginx
        print("Configuring Nginx...")
        nginx_conf = f"""
server {{
    listen 80;
    server_name {DOMAIN} www.{DOMAIN};

    location / {{
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
        # Write nginx conf locally then upload
        with open("niro_nginx", "w") as f:
            f.write(nginx_conf)
        
        sftp.put("niro_nginx", f"/etc/nginx/sites-available/{DOMAIN}")
        run_command(ssh, f"ln -sf /etc/nginx/sites-available/{DOMAIN} /etc/nginx/sites-enabled/")
        run_command(ssh, "rm -f /etc/nginx/sites-enabled/default")
        run_command(ssh, "nginx -t")
        run_command(ssh, "systemctl restart nginx")
        
        # 6. Run Certbot (SSL)
        # Note: This might fail if DNS is not propagated. We'll try it.
        print("Setting up SSL with Certbot...")
        # Non-interactive mode
        run_command(ssh, f"certbot --nginx -d {DOMAIN} --non-interactive --agree-tos -m admin@{DOMAIN} --redirect")
        
        # 7. Run Application (Gunicorn)
        print("Starting Application...")
        # Kill existing gunicorn
        run_command(ssh, "pkill gunicorn || true")
        # Run in background
        run_command(ssh, f"cd {REMOTE_DIR} && nohup gunicorn -w 4 -b 127.0.0.1:8001 server:app > app.log 2>&1 &")
        
        print("Deployment completed successfully!")
        print(f"App should be accessible at https://{DOMAIN}")
        
    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        if 'ssh' in locals(): ssh.close()
        if os.path.exists(zip_name): os.remove(zip_name)
        if os.path.exists("niro_nginx"): os.remove("niro_nginx")

if __name__ == "__main__":
    deploy()
