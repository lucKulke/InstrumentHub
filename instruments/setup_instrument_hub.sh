#!/bin/bash

# Function to display usage instructions
usage() {
  echo "Usage: $0 <instrument_name> [--user <username>]"
  echo "  <instrument_name>  The name of the instrument to set up (e.g., 'temperature_sensor')."
  echo "  --user <username>  (Optional) Specify the user on the Raspberry Pi (default is 'pi')."
  exit 1
}

# Parse input arguments
USER="admin"  # Default user is 'pi'
while [[ "$1" =~ ^- ]]; do
  case "$1" in
    --user)  # If --user flag is passed, set the username
      USER="$2"
      shift 2
      ;;
    *)  # Unknown option, show usage
      usage
      ;;
  esac
done

# Ensure the script is passed an argument for the instrument name
if [ -z "$1" ]; then
  echo "Error: <instrument_name> is required."
  usage
fi

# Define Variables
REPO_URL="https://github.com/lucKulke/InstrumentHub/raw/main"  # Raw GitHub URL
PROJECT_DIR="/home/$USER/instrument_hub"  # Directory where the project will be set up
INSTRUMENT_NAME="$1"  # The name of the instrument (passed as an argument)
SERVICE_NAME="instrument_hub.service"
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME"

# Update & Install dependencies
echo "Updating system and installing dependencies..."
sudo apt update -y && sudo apt upgrade -y
sudo apt install -y curl python3-pip python3-venv unzip

# Install Bun (Node package manager)
echo "Installing Bun..."
curl -fsSL https://bun.sh/install | bash

# Ensure that Bun is installed and added to PATH
export PATH="$HOME/.bun/bin:$PATH"

# Set up project directory for the chosen user
echo "Setting up project directory for user '$USER'..."
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Download the base folder (code common to all instruments) as a ZIP archive
echo "Downloading base folder..."
curl -L "https://github.com/yourusername/yourrepo/archive/refs/heads/main.zip" -o base.zip
unzip base.zip
mv yourrepo-main/instruments/base "$PROJECT_DIR/base"
rm -rf yourrepo-main base.zip

# Download the driver for the specific instrument
echo "Downloading driver for $INSTRUMENT_NAME..."
curl -LO "$REPO_URL/instruments/drivers/$INSTRUMENT_NAME/driver.py"

# Set up Python virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies (requirements.txt should exist in base folder)
echo "Installing Python dependencies..."
curl -LO "$REPO_URL/instruments/base/requirements.txt"
pip install -r requirements.txt

# Install Bun dependencies (if you have a package.json)
bun install

# Create a systemd service file for the specified user
echo "Creating systemd service for user '$USER'..."
sudo tee "$SERVICE_PATH" > /dev/null <<EOL
[Unit]
Description=Instrument Hub Service
After=network.target

[Service]
User=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/base/app.py
Restart=always
Environment=PATH=$PROJECT_DIR/venv/bin:$PATH

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd to apply the service
echo "Reloading systemd to apply the service..."
sudo systemctl daemon-reload

# Enable and start the service
echo "Enabling and starting the service..."
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

# Check the status of the service
echo "Checking service status..."
sudo systemctl status $SERVICE_NAME

echo "Setup complete!"
