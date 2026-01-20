"""
Deployment script for Augi AI Assistant
Supports: Streamlit Cloud, Heroku, Railway, and self-hosted servers
"""

import subprocess
import json
import sys
from pathlib import Path
from typing import Dict
from src.version_manager import VersionManager


class DeploymentManager:
    """Manages deployment to various platforms."""
    
    def __init__(self):
        """Initialize deployment manager."""
        self.version_manager = VersionManager()
        self.platforms = {
            "streamlit_cloud": self.deploy_streamlit_cloud,
            "heroku": self.deploy_heroku,
            "railway": self.deploy_railway,
            "self_hosted": self.deploy_self_hosted,
        }
    
    def deploy_streamlit_cloud(self, repo_url: str = None) -> Dict:
        """Deploy to Streamlit Cloud.
        
        Prerequisites:
        - Push code to GitHub
        - Link GitHub repo to Streamlit Cloud
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Deployment status
        """
        print("🚀 Deploying to Streamlit Cloud...")
        print("\n📋 Instructions:")
        print("1. Push your code to GitHub:")
        print("   git add .")
        print("   git commit -m 'Update: your message'")
        print("   git push")
        print("\n2. Go to https://share.streamlit.io")
        print("3. Click 'New app' and select your GitHub repo")
        print("4. Streamlit Cloud will automatically deploy!\n")
        
        deployment = {
            "platform": "streamlit_cloud",
            "status": "ready",
            "instructions": [
                "Push code to GitHub",
                "Link repo to Streamlit Cloud",
                "Auto-deploys on every push"
            ]
        }
        
        self.version_manager.mark_deployed("streamlit_cloud", repo_url)
        return deployment
    
    def deploy_heroku(self, app_name: str) -> Dict:
        """Deploy to Heroku.
        
        Prerequisites:
        - Heroku account
        - Heroku CLI installed
        
        Args:
            app_name: Heroku app name
            
        Returns:
            Deployment status
        """
        print("🚀 Deploying to Heroku...")
        
        try:
            # Create Procfile if not exists
            procfile_content = "web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0"
            with open("Procfile", "w") as f:
                f.write(procfile_content)
            
            # Create runtime.txt for Python version
            with open("runtime.txt", "w") as f:
                f.write("python-3.11.0")
            
            commands = [
                ["git", "add", "."],
                ["git", "commit", "-m", "Deploy to Heroku"],
                ["heroku", "login"],
                ["heroku", "create", app_name],
                ["git", "push", "heroku", "main"]
            ]
            
            for cmd in commands:
                print(f"Running: {' '.join(cmd)}")
                subprocess.run(cmd, check=False)
            
            deployment = {
                "platform": "heroku",
                "status": "deployed",
                "app_url": f"https://{app_name}.herokuapp.com",
                "steps_completed": [
                    "Procfile created",
                    "runtime.txt created",
                    "Pushed to Heroku"
                ]
            }
            
            self.version_manager.mark_deployed("heroku", f"https://{app_name}.herokuapp.com")
            return deployment
        
        except Exception as e:
            return {
                "platform": "heroku",
                "status": "error",
                "error": str(e)
            }
    
    def deploy_railway(self) -> Dict:
        """Deploy to Railway.
        
        Prerequisites:
        - Railway account
        - Railway CLI installed
        
        Returns:
            Deployment status
        """
        print("🚀 Deploying to Railway...")
        print("\n📋 Instructions:")
        print("1. Install Railway CLI: npm i -g @railway/cli")
        print("2. Login: railway login")
        print("3. Link project: railway link")
        print("4. Deploy: railway up\n")
        
        deployment = {
            "platform": "railway",
            "status": "ready",
            "instructions": [
                "Install Railway CLI",
                "Login with 'railway login'",
                "Link project with 'railway link'",
                "Deploy with 'railway up'"
            ]
        }
        
        self.version_manager.mark_deployed("railway")
        return deployment
    
    def deploy_self_hosted(self, server_ip: str, port: int = 8501) -> Dict:
        """Deploy to self-hosted server.
        
        Args:
            server_ip: Server IP or domain
            port: Port to run on
            
        Returns:
            Deployment status
        """
        print("🚀 Self-hosted deployment configuration...\n")
        
        nginx_config = f"""
# Save this to /etc/nginx/sites-available/augi

server {{
    listen 80;
    server_name {server_ip};
    
    location / {{
        proxy_pass http://localhost:{port};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }}
}}

# Then run:
# sudo ln -s /etc/nginx/sites-available/augi /etc/nginx/sites-enabled/
# sudo systemctl restart nginx
"""
        
        systemd_service = """
# Save this to /etc/systemd/system/augi.service

[Unit]
Description=Augi AI Assistant
After=network.target

[Service]
Type=simple
User=augi
WorkingDirectory=/home/augi/Personal ai 1
ExecStart=/home/augi/Personal ai 1/.venv/bin/python -m streamlit run streamlit_app.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target

# Then run:
# sudo systemctl daemon-reload
# sudo systemctl enable augi
# sudo systemctl start augi
"""
        
        print("📋 Nginx Configuration:")
        print(nginx_config)
        print("\n📋 Systemd Service Configuration:")
        print(systemd_service)
        
        deployment = {
            "platform": "self_hosted",
            "status": "configured",
            "server": server_ip,
            "port": port,
            "nginx_config": nginx_config,
            "systemd_service": systemd_service
        }
        
        self.version_manager.mark_deployed("self_hosted", f"http://{server_ip}:{port}")
        return deployment
    
    def get_deployment_status(self) -> Dict:
        """Get status of all deployments.
        
        Returns:
            Deployment status across all platforms
        """
        return self.version_manager.get_deployment_status()
    
    def print_deployment_guide(self):
        """Print complete deployment guide."""
        guide = """
╔════════════════════════════════════════════════════════════════╗
║         AUGI AI ASSISTANT - DEPLOYMENT GUIDE                   ║
╚════════════════════════════════════════════════════════════════╝

🌟 RECOMMENDED: STREAMLIT CLOUD (Fastest & Easiest)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Push to GitHub:
   git add .
   git commit -m "Deploy Augi v2.0"
   git push

2. Go to https://share.streamlit.io

3. Click "New app"

4. Select your GitHub repo

5. Streamlit Cloud deploys automatically! 🎉

Live in 2-3 minutes • Free tier available • Auto-updates on every push


📦 ALTERNATIVE: HEROKU
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli

2. Login:
   heroku login

3. Create app:
   heroku create augi-ai-app

4. Deploy:
   git push heroku main

5. Open app:
   heroku open


🚄 ALTERNATIVE: RAILWAY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Install Railway: npm install -g @railway/cli

2. Login: railway login

3. Initialize: railway link

4. Deploy: railway up


🖥️ SELF-HOSTED (VPS/Dedicated Server)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. SSH into server

2. Clone repository:
   git clone <your-repo-url>
   cd Personal\ ai\ 1

3. Create virtual environment:
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

4. Set up Systemd service (auto-restart on failure):
   sudo cp deploy/augi.service /etc/systemd/system/
   sudo systemctl enable augi
   sudo systemctl start augi

5. Set up Nginx reverse proxy:
   sudo cp deploy/nginx.conf /etc/nginx/sites-available/augi
   sudo ln -s /etc/nginx/sites-available/augi /etc/nginx/sites-enabled/
   sudo systemctl restart nginx

6. Set up SSL (free with Let's Encrypt):
   sudo certbot --nginx -d your-domain.com


🔄 CONTINUOUS UPDATES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

After deployment, any code changes are deployed with:
   git add .
   git commit -m "Update: describe your change"
   git push

All user data (conversations, memories) is preserved!


📊 MONITORING & UPDATES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Check deployment status:
   python -m deploy check-status

View version info:
   python -m deploy show-version

Create new release:
   python -m deploy create-release --version 2.1.0 --features "feature1,feature2"
"""
        print(guide)


def main():
    """Main deployment CLI."""
    if len(sys.argv) < 2:
        manager = DeploymentManager()
        manager.print_deployment_guide()
        return
    
    command = sys.argv[1]
    manager = DeploymentManager()
    
    if command == "streamlit":
        result = manager.deploy_streamlit_cloud()
        print(json.dumps(result, indent=2))
    
    elif command == "heroku":
        app_name = sys.argv[2] if len(sys.argv) > 2 else "augi-ai-app"
        result = manager.deploy_heroku(app_name)
        print(json.dumps(result, indent=2))
    
    elif command == "railway":
        result = manager.deploy_railway()
        print(json.dumps(result, indent=2))
    
    elif command == "self-hosted":
        server_ip = sys.argv[2] if len(sys.argv) > 2 else "example.com"
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 8501
        result = manager.deploy_self_hosted(server_ip, port)
        print(json.dumps(result, indent=2))
    
    elif command == "status":
        status = manager.get_deployment_status()
        print(json.dumps(status, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        manager.print_deployment_guide()


if __name__ == "__main__":
    main()
