import paramiko
import time

host = "157.173.110.101"
user = "root"
password = "admindenequi12"

def execute_command(ssh, command, description):
    print(f"Executing: {description}...")
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print(f"Success: {description}")
        return True
    else:
        print(f"Error: {description}")
        err = stderr.read().decode()
        print(err)
        return False

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {host}...")
    ssh.connect(host, username=user, password=password)
    print("Connected!")

    # 1. Update and Install Git/Python/Cloudflared deps
    execute_command(ssh, "apt-get update", "Update package list")
    execute_command(ssh, "apt-get install -y git python3-pip python3-venv wget", "Install system dependencies")

    # 2. Clone Repo
    stdin, stdout, stderr = ssh.exec_command("ls -d /root/NIRO")
    if stdout.channel.recv_exit_status() != 0:
        execute_command(ssh, "git clone https://github.com/scamero1/NIRO.git /root/NIRO", "Clone NIRO repository")
    else:
        print("Repo already exists, pulling latest...")
        execute_command(ssh, "cd /root/NIRO && git pull", "Pull latest changes")

    # 3. Setup Virtual Environment and Install Dependencies
    print("Setting up virtual environment...")
    # Check if venv exists
    stdin, stdout, stderr = ssh.exec_command("ls -d /root/NIRO/venv")
    if stdout.channel.recv_exit_status() != 0:
        execute_command(ssh, "cd /root/NIRO && python3 -m venv venv", "Create venv")
    
    execute_command(ssh, "/root/NIRO/venv/bin/pip install -r /root/NIRO/requirements.txt", "Install Python requirements")

    # 4. Start Server (Kill existing first if any)
    execute_command(ssh, "pkill -f server.py", "Stop existing server")
    
    # Start in background
    print("Starting NIRO server...")
    ssh.exec_command("cd /root/NIRO && nohup venv/bin/python server.py > server.log 2>&1 &")
    time.sleep(3)
    
    # Verify it's running
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep server.py | grep -v grep")
    running_procs = stdout.read().decode()
    if running_procs:
        print("NIRO server is running!")
        print(running_procs)
    else:
        print("Failed to start NIRO server. Checking logs...")
        stdin, stdout, stderr = ssh.exec_command("cat /root/NIRO/server.log")
        print(stdout.read().decode())

    # 5. Install Cloudflared
    print("Installing Cloudflared...")
    check_cf = "command -v cloudflared"
    stdin, stdout, stderr = ssh.exec_command(check_cf)
    if stdout.channel.recv_exit_status() != 0:
        cmds = [
            "wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb",
            "dpkg -i cloudflared-linux-amd64.deb",
            "rm cloudflared-linux-amd64.deb"
        ]
        execute_command(ssh, " && ".join(cmds), "Install Cloudflared")
    else:
        print("Cloudflared already installed.")

    print("\n--- Setup Complete ---")
    
    ssh.close()

except Exception as e:
    print(f"Connection failed: {e}")
