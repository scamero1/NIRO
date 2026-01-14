import paramiko

host = "157.173.110.101"
user = "root"
password = "admindenequi12"
local_file = "index_pro.html"
remote_file = "/root/NIRO/index.html"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print(f"Connecting to {host}...")
ssh.connect(host, username=user, password=password)

print(f"Uploading {local_file}...")
sftp = ssh.open_sftp()
sftp.put(local_file, remote_file)
print(f"Uploading sw.js...")
sftp.put("sw.js", "/root/NIRO/sw.js")
print(f"Uploading manifest.json...")
sftp.put("manifest.json", "/root/NIRO/manifest.json")
print(f"Uploading server.py...")
sftp.put("server.py", "/root/NIRO/server.py")
sftp.close()

# Try to restart server if running with systemd (best effort)
# Or just kill python and restart? That might be risky if we are not in a screen session.
# Assuming user runs it manually or via screen.
# Let's just upload for now.
ssh.close()
print("Upload complete.")
