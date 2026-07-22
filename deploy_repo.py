import os
import sys
import ssl
import json
import urllib.request
import subprocess

ENV_FILE = "/Users/saitejabandaru/.gemini/antigravity/scratch/.env"

def get_token():
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, 'r') as f:
            for line in f:
                if line.startswith("GITHUB_TOKEN="):
                    return line.split("=")[1].strip()
    return os.environ.get("GITHUB_TOKEN")

def run_cmd(cmd_list, env=None):
    if env is None:
        env = os.environ.copy()
    env["GIT_CONFIG_GLOBAL"] = "/dev/null"
    env["GIT_CONFIG_SYSTEM"] = "/dev/null"
    res = subprocess.run(cmd_list, capture_output=True, text=True, env=env)
    if res.returncode != 0:
        print(f"Git Warning/Error: {res.stderr.strip()}")
    else:
        print(f"✓ {res.stdout.strip() or 'Command succeeded'}")
    return res

def main():
    token = get_token()
    if not token:
        print("✗ GITHUB_TOKEN not found!")
        sys.exit(1)
        
    repo_name = "openssf-critical-infrastructure"
    
    # Custom environment for git without accessing /Users/saitejabandaru/.gitconfig
    env = os.environ.copy()
    env["GIT_CONFIG_GLOBAL"] = "/dev/null"
    env["GIT_CONFIG_SYSTEM"] = "/dev/null"
    
    print("Initializing git repository...")
    run_cmd(["git", "init"], env=env)
    run_cmd(["git", "config", "user.name", "Sai Teja Bandaru"], env=env)
    run_cmd(["git", "config", "user.email", "saitejabandaru.ds@gmail.com"], env=env)
    run_cmd(["git", "add", "."], env=env)
    run_cmd(["git", "commit", "-m", "feat: initial release of OpenSSF Criticality Analytics Platform (Score >= 0.400)"], env=env)
    run_cmd(["git", "branch", "-M", "main"], env=env)
    
    remote_url = f"https://saitejabandaru-in:{token}@github.com/saitejabandaru-in/{repo_name}.git"
    run_cmd(["git", "remote", "remove", "origin"], env=env)
    run_cmd(["git", "remote", "add", "origin", remote_url], env=env)
    
    print("Pushing directly to GitHub main branch...")
    push_res = run_cmd(["git", "push", "-u", "origin", "main", "--force"], env=env)
    if push_res.returncode == 0:
        print(f"\n🎉 SUCCESS: Repository live at https://github.com/saitejabandaru-in/{repo_name}")
    else:
        print(f"Push Error: {push_res.stderr}")

if __name__ == "__main__":
    main()
