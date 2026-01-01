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

def run_command(ssh, command):
    print(f"Running: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print(f"OUT: {out}")
    if err: print(f"ERR: {err}")
    return exit_status

def deploy_fix():
    try:
        print(f"Connecting to {HOST}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=PASS)
        
        # 1. Setup Venv to avoid system package conflicts
        print("Setting up virtual environment...")
        run_command(ssh, "apt-get install -y python3-venv")
        run_command(ssh, f"cd {REMOTE_DIR} && python3 -m venv venv")
        
        # 2. Install dependencies in venv
        print("Installing dependencies in venv...")
        # Upgrade pip first
        run_command(ssh, f"cd {REMOTE_DIR} && venv/bin/pip install --upgrade pip")
        run_command(ssh, f"cd {REMOTE_DIR} && venv/bin/pip install -r requirements.txt gunicorn")
        
        # 3. Update Nginx Config to include IP address
        print("Updating Nginx config to allow IP access...")
        nginx_conf = f"""
server {{
    listen 80;
    server_name {DOMAIN} www.{DOMAIN} {HOST};
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
        sftp = ssh.open_sftp()
        with open("niro_nginx_fix", "w") as f:
            f.write(nginx_conf)
        
        sftp.put("niro_nginx_fix", f"/etc/nginx/sites-available/{DOMAIN}")
        run_command(ssh, "nginx -t")
        run_command(ssh, "systemctl restart nginx")
        
        # 4. Restart Gunicorn using venv
        print("Restarting Gunicorn...")
        run_command(ssh, "pkill gunicorn || true")
        time.sleep(2)
        run_command(ssh, f"cd {REMOTE_DIR} && nohup venv/bin/gunicorn -w 4 -b 127.0.0.1:8001 server:app > app.log 2>&1 &")
        
        # 5. Verify local
        print("Verifying deployment locally on server...")
        run_command(ssh, "curl -I http://127.0.0.1:8001")
        
        print("\n---------------------------------------------------")
        print("Fix applied!")
        print(f"Try accessing via IP: http://{HOST}")
        print(f"Try accessing via Domain: http://{DOMAIN}")
        print("Note: SSL (https) requires DNS propagation.")
        print("---------------------------------------------------")

    except Exception as e:
        print(f"Fix failed: {e}")
    finally:
        if 'ssh' in locals(): ssh.close()
        if os.path.exists("niro_nginx_fix"): os.remove("niro_nginx_fix")

if __name__ == "__main__":
    deploy_fix()
