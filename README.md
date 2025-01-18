# Map-Reduce Protocol Implementation

This project is a Python implementation of the Map-Reduce protocol, designed to facilitate distributed computing. It utilizes Pyro4 for remote procedure calls and a Chord-based Distributed Hash Table (DHT) for efficient data management.

## Table of Contents
- [Requirements](#requirements)
- [Setup](#setup)
- [Usage](#usage)
  - [Starting the Server](#starting-the-server)
  - [Running the Client](#running-the-client)
- [API Reference](#api-reference)
- [Logging](#logging)
- [Contributing](#contributing)
- [License](#license)

## Requirements

### System Requirements
- Docker image: `python:3.9.7-alpine`
  - To pull the image (with internet connection):
    ```bash
    docker pull python:3.9.7-alpine
    ```
  - Or load from a provided tar image:
    ```bash
    docker load -i <img_path>
    ```

- Create a Docker network named "distributed":
    ```bash
    docker network create --driver=bridge --subnet=172.18.0.0/16 --ip-range=172.18.1.0/25 --gateway=172.18.1.254 distributed
    ```

## Setup

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```

2. Ensure Docker is running and the network is created as specified above.

## Usage

### Starting the Server

To start the server, navigate to the project root and run the following command, replacing `k` with the number of server instances you want to run:
```bash
./scripts/batch_run server k -dt
```

### Running the Client

To start a client request, execute:
```bash
./scripts/run_client
```

The client script located in `./map_reduce/client/client.py` requires initial data in the format `[(IN_KEY, IN_VALUE)]`, along with the `map` and `reduce` functions defined as follows:

```python
def map(in_key: IN_KEY, in_value: IN_VALUE) -> [(OUT_KEY, MID_VALUE)]:
    pass

def reduce(out_key: OUT_KEY, values: [MID_VALUE]) -> OUT_VAL:
    pass
```

The provided API will return the results of the MapReduce procedure through `ServerInterface.await_results()`, yielding a `dict` or key/value pair iterable of type signature `{ OUT_KEY: OUT_VAL }`.

## API Reference

- **Map Function**: Processes input key-value pairs and produces intermediate key-value pairs.
- **Reduce Function**: Aggregates intermediate values by key to produce final output values.

## Logging

The application uses a logging mechanism to track server activities and errors. Logs can be found in the designated log files or console output, depending on your configuration.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes. Ensure that your code adheres to the project's coding standards and includes appropriate tests.
