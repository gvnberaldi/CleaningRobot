# Cleaning Robot
A Python-based RESTful API for managing a cleaning robot within a grid-based environment. It provides functionalities for configuring maps, executing cleaning routines, and maintaining a history of cleaning sessions.

This project follows DevOps best practices, incorporating Continuous Integration/Continuous Deployment (CI/CD), Domain-Driven Design (DDD), and Test-Driven Development (TDD). The application is designed for efficient and automated deployment using Docker and Docker Compose.

# Application Deployment Guide

## Prerequisites
To run this application, you need to have **Docker** and **Docker Compose** installed on your system.

### Installing Docker & Docker Compose
#### **Windows & Mac**
- Download and install **Docker Desktop** from the official website:  
  [https://www.docker.com/get-started](https://www.docker.com/get-started)
- Docker Compose is included with Docker Desktop.

#### **Linux**
Run the following commands to install Docker and Docker Compose:
```bash
# Install Docker
curl -fsSL https://get.docker.com | sudo bash

# Install Docker Compose (latest version)
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make Docker Compose executable
sudo chmod +x /usr/local/bin/docker-compose
```

Verify installation:
```bash
docker --version
docker-compose --version
```

## Cloning and Running the Application
Once Docker and Docker Compose are installed, follow these steps to deploy the application:

1. Clone the repository:
   ```bash
   git clone https://github.com/gvnberaldi/CleaningRobot.git
   ```
2. Move into the cloned folder:
   ```bash
   cd CleaningRobot
   ```
3. Run the application using Docker Compose:
   ```bash
   docker-compose up -d
   ```

This command will automatically pull the necessary Docker image from **Docker Hub**, build the application, and start it in detached mode (`-d`).

## Accessing the Application
After deployment, the application will be accessible at:
```
http://localhost:5000
```
Ensure that port **5000** is available on your system.

## Stopping the Application
To stop the application, run:
```bash
docker-compose down
```
This will gracefully stop and remove the running containers.

## Application Usage

This application provides two different robot cleaning modes: a **Base Robot** and a **Premium Robot**. The Premium Robot avoids cleaning tiles that were cleaned in previous sessions, as well as tiles already cleaned in the current session.

### 1. Setting the Robot Map
Before starting a cleaning session, you must set the robot map. This is mandatory for both the **Base Robot** and the **Premium Robot**. Without setting a map, a cleaning session cannot be initiated.

#### **Setting the Map for Base Robot**
```bash
curl -X POST -F "file=@your_map_file.[txt,json]" http://localhost:5000/set-map
```
#### **Setting the Map for Premium Robot**
```bash
curl -X POST -F "file=@your_map_file.[txt,json]" http://localhost:5000/set-map-premium
```

Both the set-map and set-map-premium endpoints require a TXT or JSON file as input representing the map:

**Example TXT Map File:**
```
xxooxx
xoooox
xxooxx
oooooo
xxooxx
```
Where:
- `x` represents obstacles
- `o` represents cleanable tiles

**Example JSON Map File:**
```json
{
  "rows": 5,
  "cols": 5,
  "tiles": [
    { "x": 0, "y": 0, "walkable": true },
    { "x": 1, "y": 0, "walkable": true },
    ...
  ]
}
```

**Usage Example:**
```bash
curl -X POST -F "file=@/path/to/your/map.txt" http://localhost:5000/set-map
```

### 2. Starting a Cleaning Session
After setting the map, you can start a cleaning session using either the **Base Robot** or the **Premium Robot**.

#### **Starting a Cleaning Session with Base Robot**
```bash
curl -X POST -F "file=@your_actions_file.[txt,json]" http://localhost:5000/clean
```
#### **Starting a Cleaning Session with Premium Robot**
```bash
curl -X POST -F "file=@your_actions_file.[txt,json]" http://localhost:5000/clean-premium
```

Both the clean and clean-premium endpoints require a TXT or JSON file as input representing the actions that the robot should follow:

**Example TXT Actions File:**
```
6 2
east 4
south 1
north 1
west 5
```
The first line represents the robot's starting position (`x y`).
Each subsequent line contains a movement command (`direction steps`).

**Example JSON Actions File:**
```json
{
  "x": 2,
  "y": 4,
  "actions": [
    { "direction": "north", "steps": 10 },
    { "direction": "east", "steps": 5 }
  ]
}
```

**Usage Example:**
```bash
curl -X POST -F "file=@/path/to/your/actions.json" http://localhost:5000/clean
```

### 3. Downloading Cleaning History
Each cleaning session, whether performed by the Base Robot or the Premium Robot, is stored in a permanent **PostgreSQL** database. For simplicity, both Base and Premium cleaning sessions are stored in the same table.

The history of all cleaning sessions can be retrieved using the `get-history` endpoint:

```bash
curl -o output.csv http://localhost:5000/history
```
This command will download in the current directory the cleaning history as a CSV file (`output.csv`). 
The file will contain an error message if no history is available in the database.

# Future Improvements

Currently, the application runs locally using Docker and Docker Compose. A future improvement is to automate its deployment to cloud environments such as **AWS Elastic Container Service (ECS)**, ensuring a smooth and efficient rollout of new versions.