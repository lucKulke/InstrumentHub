# Kleinmaelzung

## System Overview
This project facilitates real-time communication between scientific microcontrollers (e.g., Raspberry Pis that are connected to instruments via serial interface), a central server, and client applications, using WebSocket protocols for seamless, bidirectional data transfer. The system architecture is designed to allow clients to monitor and control instruments remotely through the server, making it ideal for scientific applications that require continuous data streaming and interactive control.

## System Flow
### 1. Instrument-to-Microcontroller Connection:

Each scientific instrument is connected to a microcontroller (e.g. a Raspberry Pi) via an appropriate communication interface (e.g. serial (usb, rs232)).
The microcontroller is responsible for collecting data from the instrument and forwarding it to the central server.

### 2. Microcontroller-to-Server Communication:

The microcontroller establishes a persistent WebSocket connection to the server.
This WebSocket connection allows the microcontroller to continuously send data from the instrument to the server in real-time.
It also enables the server to send control commands back to the microcontroller, which are then relayed to the instrument.

### 3. Server as a Central Hub:

The server acts as a central hub for all data traffic, managing WebSocket connections from both microcontrollers and clients.
When an instrument sends data via the microcontroller, the server immediately forwards this data to any connected client that is subscribed to that instrument’s data stream.

### 4. Client-to-Server Communication:

Clients can connect to the server over WebSocket to listen to live data from specific instruments.
Clients can select which instruments they want to monitor, and the server will route relevant data from those instruments to the client in real-time.
The WebSocket protocol also enables clients to send commands to instruments via the server, providing two-way communication for control and configuration purposes.

### Key Features
Bi-directional Communication: WebSocket connections enable both data monitoring and command sending, making the system highly interactive.
Centralized Management: The server coordinates data flow between multiple instruments, microcontrollers, and clients.
Scalability: Additional instruments and clients can be added as needed, making the system flexible for larger deployments.


## Diagrams showing overall system flow
This diagram outlines the main components and their connections in the system.

```mermaid
graph TD
    subgraph Instruments
        A1[Instrument 1]
        A2[Instrument 2]
        A3[Instrument 3]
    end
    subgraph Microcontrollers
        B1[Controller 1]
        B2[Controller 2]
        B3[Controller 3]
    end
    subgraph Server
        C[Central Server]
    end
    subgraph Clients
        D1[Client 1]
        D2[Client 2]
    end
    
    A1 -->|usb| B1
    A2 -->|rs232| B2
    A3 -->|i2c| B3
    B1 -->|WebSocket| C
    B2 -->|WebSocket| C
    B3 -->|WebSocket| C
    C -->|WebSocket| D1
    C -->|WebSocket| D2
```
2. Data Flow Diagram
This diagram illustrates how data flows through the system from instruments to clients, with the server as the intermediary.

```mermaid
sequenceDiagram
    participant Instrument
    participant Microcontroller
    participant Server
    participant Client

    Instrument->>Microcontroller: Send Data
    Microcontroller->>Server: Forward Data (WebSocket)
    Server->>Client: Stream Data (WebSocket)
```
3. Command Flow Diagram
This shows how commands from a client can be sent back to the instruments through the server and microcontroller.

```mermaid
sequenceDiagram
    participant Client
    participant Server
    participant Microcontroller
    participant Instrument

    Client->>Server: Send Command (WebSocket)
    Server->>Microcontroller: Forward Command (WebSocket)
    Microcontroller->>Instrument: Execute Command
```


### Additional features:
1. Data Traffic Logging:

    - The server includes a logging feature that records all incoming and outgoing data traffic between the instruments, microcontrollers, and clients.
    - This feature allows for tracking of data transmission history, which can be useful for diagnostics, troubleshooting, and historical data analysis.


2. Calibration Protocol Generation:

    - The server can create calibration protocols for instruments, allowing users to standardize and document calibration processes.
    - The protocol can be downloaded as a PDF, making it easy to print or share for compliance and record-keeping purposes.


