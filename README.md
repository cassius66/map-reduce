# MapReduce Framework

A distributed MapReduce implementation in Python using Pyro4 for remote procedure calls and a Chord-based DHT for data management.

## Features

- Distributed processing with load balancing
- Fault-tolerant architecture
- Data distribution using Chord DHT
- Data replication
- Task progress monitoring
- Structured logging with rotation
- Docker support

## Prerequisites

- Python 3.9+
- Docker
- Git

## Installation

1. Clone the repository:
```bash
git clone https://github.com/cassius66/map-reduce.git
cd map-reduce
```

2. Create Docker network:
```bash
docker network create --driver=bridge --subnet=172.18.0.0/16 --ip-range=172.18.1.0/25 --gateway=172.18.1.254 distributed
```

3. Install dependencies:
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Running with Docker

1. Build the image:
```bash
docker build -t map-reduce .
```

2. Run a cluster:
```bash
# Start master node
docker run -d --name master --network distributed map-reduce python main.py server

# Start worker nodes
docker run -d --name worker1 --network distributed map-reduce python main.py server
docker run -d --name worker2 --network distributed map-reduce python main.py server
```

3. View logs:
```bash
docker logs -f master
```

### Running Locally

1. Start server nodes:
```bash
./scripts/batch_run server 3 -dt
```

2. Run the example:
```bash
python examples/word_count.py --file examples/sample.txt
```

## Examples

### Word Count Example

```python
from map_reduce.client.server_interface import ServerInterface

# Input data
text_data = [
    "hello world",
    "hello distributed computing",
    "world of mapreduce"
]

def map(line_num: int, line: str) -> list[tuple[str, int]]:
    return [(word, 1) for word in line.split()]

def reduce(word: str, counts: list[int]) -> int:
    return sum(counts)

# Run MapReduce
server = ServerInterface()
daemon = server.startup(text_data, map, reduce)
if daemon:
    print("Processing...")
    results = server.await_results()
    print("Word counts:", results)
```

## Architecture

The framework consists of:

1. Master Node: Coordinates task distribution
2. Worker Nodes: Execute map and reduce tasks
3. DHT Layer: Handles data storage and retrieval

### Logging

The framework uses structured logging with:

- Console and file output
- Log rotation (10MB per file, 5 backup files)
- Optional JSON formatting
- Configurable log levels per component

Example configuration:
```python
LOGGING = {
    "master": {
        "level": "INFO",
        "json_format": True,
        "log_file": "logs/master.log"
    },
    "worker": {
        "level": "DEBUG",
        "json_format": False
    }
}
```

## Configuration

Key settings in `map_reduce/server/configs.py`:

```python
REQUEST_TIMEOUT = 0.5        # Request timeout in seconds
MAX_TASK_TIMEOUT = 300      # Maximum task execution time
ITEMS_PER_CHUNK = 16        # Items processed per map task
DHT_REPLICATION_SIZE = 5    # Number of data replicas
```
