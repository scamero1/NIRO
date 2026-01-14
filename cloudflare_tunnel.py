import paramiko

HOST = "157.173.110.101"
USER = "root"
PASS = "admindenequi12"
REMOTE_LOG = "/var/log/cloudflared.log"


def run_command(ssh, command):
    print(f"Running: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        print("OUT:")
        print(out)
    if err:
        print("ERR:")
        print(err)
    return exit_status, out, err


def recreate_quick_tunnel():
    print(f"Connecting to {HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS)

    try:
        # 1. Detener túneles antiguos y limpiar binario/log
        run_command(ssh, "pkill cloudflared || true")
        run_command(ssh, "rm -f /usr/local/bin/cloudflared {log}".format(log=REMOTE_LOG))

        # 2. Instalar binario oficial de cloudflared
        run_command(ssh, "apt-get update -qq")
        run_command(ssh, "apt-get install -y wget")
        run_command(
            ssh,
            "wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /usr/local/bin/cloudflared",
        )
        run_command(ssh, "chmod +x /usr/local/bin/cloudflared")

        # 3. Lanzar quick tunnel en segundo plano y extraer la URL
        cmd = (
            "nohup /usr/local/bin/cloudflared tunnel --no-autoupdate --url http://127.0.0.1:8001 "
            f"> {REMOTE_LOG} 2>&1 & sleep 25 && "
            f"grep -m1 -o 'https://[A-Za-z0-9.-]*trycloudflare.com' {REMOTE_LOG} || echo URL_NOT_FOUND"
        )
        _, out, _ = run_command(ssh, cmd)

        print("\n============================================================")
        print("Resultado del túnel rápido de Cloudflare:")
        print(out or "(sin salida)")
        print("============================================================")
    finally:
        ssh.close()


if __name__ == "__main__":
    recreate_quick_tunnel()

