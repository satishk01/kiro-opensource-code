#!/bin/bash

# EC2 Setup Script for Kiro Streamlit App
# Run this script on your EC2 instance to set up the environment

set -e

echo "🚀 Setting up Kiro Streamlit App on EC2..."

# Update system
echo "📦 Updating system packages..."
sudo yum update -y

# Install Docker
echo "🐳 Installing Docker..."
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
echo "🔧 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
echo "📚 Installing Git..."
sudo yum install -y git

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/kiro-app
sudo chown ec2-user:ec2-user /opt/kiro-app
cd /opt/kiro-app

# Clone or copy application code (adjust as needed)
echo "📥 Setting up application code..."
# git clone <your-repo-url> .
# Or copy files from S3, etc.

# Create necessary directories
mkdir -p logs temp uploads

# Set up environment file
echo "⚙️ Creating environment configuration..."
cat > .env << EOF
AWS_DEFAULT_REGION=us-east-1
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
PYTHONPATH=/app
LOG_LEVEL=INFO
EOF

# Create systemd service for auto-start
echo "🔄 Creating systemd service..."
sudo tee /etc/systemd/system/kiro-app.service > /dev/null << EOF
[Unit]
Description=Kiro Streamlit App
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/kiro-app
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0
User=ec2-user

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable kiro-app.service

# Set up log rotation
echo "📝 Setting up log rotation..."
sudo tee /etc/logrotate.d/kiro-app > /dev/null << EOF
/opt/kiro-app/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 ec2-user ec2-user
    postrotate
        /usr/local/bin/docker-compose -f /opt/kiro-app/docker-compose.yml restart kiro-app
    endscript
}
EOF

# Install CloudWatch agent (optional)
echo "📊 Installing CloudWatch agent..."
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
sudo rpm -U ./amazon-cloudwatch-agent.rpm

# Create CloudWatch config
sudo tee /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json > /dev/null << EOF
{
    "logs": {
        "logs_collected": {
            "files": {
                "collect_list": [
                    {
                        "file_path": "/opt/kiro-app/logs/app.log",
                        "log_group_name": "/aws/ec2/kiro-app",
                        "log_stream_name": "{instance_id}/app.log"
                    }
                ]
            }
        }
    },
    "metrics": {
        "namespace": "KiroApp",
        "metrics_collected": {
            "cpu": {
                "measurement": ["cpu_usage_idle", "cpu_usage_iowait", "cpu_usage_user", "cpu_usage_system"],
                "metrics_collection_interval": 60
            },
            "disk": {
                "measurement": ["used_percent"],
                "metrics_collection_interval": 60,
                "resources": ["*"]
            },
            "mem": {
                "measurement": ["mem_used_percent"],
                "metrics_collection_interval": 60
            }
        }
    }
}
EOF

echo "✅ EC2 setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy your application code to /opt/kiro-app"
echo "2. Update the .env file with your specific configuration"
echo "3. Start the application: sudo systemctl start kiro-app"
echo "4. Check status: sudo systemctl status kiro-app"
echo "5. View logs: docker-compose logs -f"
echo ""
echo "The application will be available at http://your-ec2-ip:8501"