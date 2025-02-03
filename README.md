# Distributed MapReduce Framework

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A high-performance distributed MapReduce implementation in Python, designed for scalable data processing across multiple nodes. Built with Pyro4 and featuring a Chord-based Distributed Hash Table (DHT) for efficient data management.

## ✨ Key Features

- 🚀 Distributed processing with automatic load balancing
- 💪 Fault-tolerant architecture with node failure recovery
- 🔄 Efficient data distribution using Chord DHT
- 🔒 Built-in data replication for reliability
- 📊 Real-time task progress monitoring
- 🛠️ Easy-to-use API for custom map/reduce functions

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Docker
- Git

### Installation

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
pip install -r requirements.txt
```

4. Build and run:
```bash
# Start 3 server nodes
./scripts/batch_run server 3 -dt

# In a new terminal, run the example
python examples/word_count.py --file examples/sample.txt
```

## 📝 Examples

The `examples` directory contains sample implementations to help you get started:

### 1. Word Count Example

A classic MapReduce example that counts word occurrences in text. Run it with:

```bash
# Run with sample text
python examples/word_count.py

# Or process your own text file
python examples/word_count.py --file path/to/your/file.txt
```

### 2. Custom Implementation

Here's a simple word count example:

```python
from map_reduce.client.server_interface import ServerInterface

# Input data
text_data = [
    "hello world",
    "hello distributed computing",
    "world of mapreduce"
]

# Define map function
def map(line_num: int, line: str) -> list[tuple[str, int]]:
    return [(word, 1) for word in line.split()]

# Define reduce function
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

Output:
```python
{
    'hello': 2,
    'world': 2,
    'distributed': 1,
    'computing': 1,
    'of': 1,
    'mapreduce': 1
}
```

## 🏗️ Architecture

The framework consists of three main components:

1. **Master Node**: Coordinates task distribution and manages the overall MapReduce process
2. **Worker Nodes**: Execute map and reduce tasks in parallel
3. **DHT Layer**: Handles distributed data storage and retrieval using Chord protocol

## 🔧 Configuration

Key configuration options in `map_reduce/server/configs.py`:

```python
REQUEST_TIMEOUT = 0.5        # Request timeout in seconds
MAX_TASK_TIMEOUT = 300      # Maximum task execution time (5 minutes)
ITEMS_PER_CHUNK = 16        # Items processed per map task
DHT_REPLICATION_SIZE = 5    # Number of data replicas for fault tolerance
```

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and commit: `git commit -m 'Add some feature'`
4. Push to your fork: `git push origin feature-name`
5. Open a Pull Request

Please ensure your code:
- Includes proper error handling
- Has type hints
- Follows PEP 8 style guide
- Includes tests for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by Google's MapReduce paper
- Built with [Pyro4](https://pyro4.readthedocs.io/) for remote procedure calls
- Uses Chord DHT algorithm for distributed data management
