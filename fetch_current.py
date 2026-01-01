import paramiko

host = "157.173.110.101"
user = "root"
password = "admindenequi12"
remote_file = "/root/NIRO/index.html"
local_file = "index_current.html"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    print(f"Connecting to {host}...")
    ssh.connect(host, username=user, password=password)
    
    print(f"Downloading {remote_file}...")
    sftp = ssh.open_sftp()
    sftp.get(remote_file, local_file)
    sftp.close()
    ssh.close()
    print("Download complete.")
except Exception as e:
    print(f"Error: {e}")
