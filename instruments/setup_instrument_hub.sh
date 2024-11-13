#!/bin/bash

# Function to display usage instructions
usage() {
  echo "Usage: $0 <instrument_name> [--user <username>] [--server_url <url>] [--instrument_id <id>]"
  echo "  <instrument_name>       The name of the instrument to set up (e.g., 'temperature_sensor')."
  echo "  --user <username>       (Optional) Specify the user on the Raspberry Pi (default is 'pi')."
  echo "  --server_url <url>      The URL of the server to connect to."
  echo "  --instrument_id <id>    The ID for the instrument."
  exit 1
}

# Default values
USER="admin"  # Default user is 'admin'
REPO_NAME="InstrumentHub"  # Default repository name
BRANCH_NAME="main"    # Default branch (you can change it if necessary)
GITHUB_USER="lucKulke"   # Replace with your desired branch name

# Parse input arguments
while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --user)
      USER="$2"
      shift 2
      ;;
    --server_url)
      SERVER_URL="$2"
      shift 2
      ;;
    --instrument_id)
      INSTRUMENT_ID="$2"
      shift 2
      ;;
    -*)
      echo "Unknown option: $1"
      usage
      ;;
    *)
      if [ -z "$INSTRUMENT_NAME" ]; then
        INSTRUMENT_NAME="$1"
        shift
      else
        echo "Unexpected argument: $1"
        usage
      fi
      ;;
  esac
done


if [ -z "$INSTRUMENT_NAME" ] || [ -z "$SERVER_URL" ] || [ -z "$INSTRUMENT_ID" ]; then
  echo "Error: <instrument_name>, --server_url, and --instrument_id are required."
  usage
fi




PROJECT_DIR="/home/$USER/instrument_hub"  # Directory where the project will be set up
SERVICE_NAME="instrument_hub.service"
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME"

# Set the GitHub raw URL for repository and branch
REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME/raw/$BRANCH_NAME"  # Raw GitHub URL


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
echo "Downloading base folder..."cd
curl -L "https://github.com/$GITHUB_USER/$REPO_NAME/archive/refs/heads/$BRANCH_NAME.zip" -o base.zip
unzip base.zip
# Move only the files from the base folder, not the folder itself
find "$REPO_NAME-$BRANCH_NAME/instruments/base" -type f -exec mv {} "$PROJECT_DIR/" \;

#mv "$REPO_NAME-$BRANCH_NAME/instruments/base" "$PROJECT_DIR"
rm -rf "$REPO_NAME-$BRANCH_NAME" base.zip

# Download the specific driver folder for the chosen instrument
echo "Downloading driver folder for $INSTRUMENT_NAME..."
curl -LO "https://github.com/$GITHUB_USER/$REPO_NAME/archive/refs/heads/$BRANCH_NAME.zip"
unzip "$BRANCH_NAME.zip" -d "$PROJECT_DIR"
echo "creating directory drivers"
mkdir "$PROJECT_DIR/drivers/"
echo "searching for '$INSTRUMENT_NAME'"

find "$REPO_NAME-$BRANCH_NAME/instruments/drivers/$INSTRUMENT_NAME" -type f -exec mv {} "$PROJECT_DIR/drivers/" \;
#mv "$REPO_NAME-$BRANCH_NAME/instruments/drivers/$INSTRUMENT_NAME" "$PROJECT_DIR/driver/"
rm -rf "$BRANCH_NAME.zip" "$REPO_NAME-$BRANCH_NAME"

echo "Creating config.json..."
cat <<EOL > "$PROJECT_DIR/config.json"
{
  "hub_ws_url": "$SERVER_URL",
  "id": "$INSTRUMENT_ID",
  "driver_runtime_path": "venv/bin/python",
  "driver_filename": "drivers/driver.py"
}
EOL



# Set up Python virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies for the base folder (requirements.txt should exist in base folder)
echo "Installing Python dependencies for base..."
pip install -r requirements.txt


# Install Python dependencies for the driver (if it has its own requirements.txt)
DRIVER_REQ_FILE="$PROJECT_DIR/drivers/requirements.txt"
if [ -f "$DRIVER_REQ_FILE" ]; then
    echo "Installing Python dependencies for the driver..."
    pip install -r "$DRIVER_REQ_FILE"
fi

# Install Bun dependencies (if you have a package.json)
bun install

# Create a systemd service file for the specified user
echo "Creating systemd service for user '$USER'..."
sudo tee "$SERVICE_PATH" > /dev/null <<EOL
[Unit]
Description=Instrument Service
After=network.target

[Service]
User=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=/home/$USER/.bun/bin/bun $PROJECT_DIR/main.js
Restart=always


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
