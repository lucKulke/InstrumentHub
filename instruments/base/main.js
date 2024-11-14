const WebSocket = require("ws");
const { spawn } = require("child_process");
const fs = require("fs");

let config;
try {
  const data = fs.readFileSync("config.json", "utf8"); // Read in config
  config = JSON.parse(data);
} catch (error) {
  console.error("Error reading config file:", error);
  process.exit(1);
}

const wsUrl = config.hub_ws_url + config.id;
const driverProcess = spawn(config.driver_runtime_path, [
  config.driver_filename,
]);
const ledProcess = spawn("venv/bin/python", ["status_led.py"]);
var ws;
var connected = false;
var reconnectInterval = 5000; // Reconnect every 5 seconds if disconnected
var reconnectAttempts = 0;
var maxReconnectAttempts = 10; // Limit to prevent excessive reconnections

// Function to initialize the WebSocket connection
function connectWebSocket() {
  // Avoid reconnecting if there is an active connection attempt
  if (ws && ws.readyState === WebSocket.CONNECTING) {
    console.log("Already attempting to connect. Waiting...");
    return;
  }

  ws = new WebSocket(wsUrl);

  ws.on("message", (message) => {
    console.log(`Received message from server: ${message}`);
    let string_message = message.toString();
    if (
      string_message.match(/find_my_instrument_(red|green)_(\d+(\.\d+)?)_(\d+)/)
    ) {
      let message_data = string_message.split("_");
      let color = message_data[3];
      let duration = message_data[4];
      let count = message_data[5];
      let led_command = `${color}_${duration}_${count}\n`;
      console.log("led execute: " + led_command);
      ledProcess.stdin.write(led_command);
    } else if (string_message != "hi") {
      console.log("driver execute: " + string_message);
      driverProcess.stdin.write(`${string_message}\n`);
    }
  });

  ws.on("open", () => {
    //clearTimeout(timeout); // Clear the timeout as we are now connected
    connected = true;
    reconnectAttempts = 0; // Reset on successful connection
    ledProcess.stdin.write("standby_on\n");
    console.log("Connected to server");
  });

  ws.on("close", async () => {
    console.log("WebSocket connection closed");
    connected = false;
    ledProcess.stdin.write("standby_off\n");
    await reconnect(); // Try to reconnect when connection closes
  });
}

// Function to reconnect WebSocket
async function reconnect() {
  if (connected) return;

  let backoffTime;
  if (reconnectAttempts >= maxReconnectAttempts) {
    console.log("Max reconnection attempts reached. Reconnecting every hour.");
    backoffTime = 3600000; // 1 hour
  } else {
    reconnectAttempts++;
    backoffTime = reconnectInterval * reconnectAttempts;
    console.log(
      `Attempting to reconnect (#${reconnectAttempts}) in ${
        backoffTime / 1000
      } seconds...`
    );
  }

  await Bun.sleep(backoffTime);

  if (!connected) {
    for (let i = 1; i <= 3; i++) {
      ledProcess.stdin.write("red_0.1_1\n");
      ledProcess.stdin.write("green_0.1_1\n");
    }
    connectWebSocket(); // Reinitialize WebSocket connection
  }
}
// Initial connection
connectWebSocket();

// Listen for data from the Driver process
driverProcess.stdout.on("data", (data) => {
  console.log(`Received data from Driver: ${data}`);
  const payload = `{"data" : "${data}" }`;

  // Send data to the server if connected
  if (connected) {
    ws.send(payload);
    ledProcess.stdin.write("green_0.2_1\n");
  } else {
    ledProcess.stdin.write("red_0.5_2\n");
  }
});

// Handle Driver process errors
driverProcess.stderr.on("data", (data) => {
  ledProcess.stdin.write("standby_off\n");
  console.error(`Driver error: ${data}`);
});

// Handle LED process errors
ledProcess.stderr.on("data", (data) => {
  console.error(`LED process error: ${data}`);
});

// Handle Driver and LED process exits
driverProcess.on("close", (code) => {
  console.log(`Driver process exited with code ${code}`);
});
ledProcess.on("close", (code) => {
  console.log(`LED process exited with code ${code}`);
});
