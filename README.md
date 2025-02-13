# map-reduce
Python implementation of the map-reduce protocol using Pyro4

## Overview
A distributed computing implementation of the MapReduce protocol using Python and Pyro4 for network communication. This project demonstrates parallel data processing through a distributed architecture.

### Features
- Distributed task processing using MapReduce paradigm
- Network communication via Pyro4
- Fault tolerance and task recovery
- Dynamic worker node management
- Support for custom map and reduce functions

## Project Structure
- `src/`: Source code directory
  - `master.py`: Master node implementation
  - `worker.py`: Worker node implementation
  - `protocol.py`: MapReduce protocol definitions
- `examples/`: Example MapReduce tasks
- `tests/`: Unit and integration tests
- `docs/`: Documentation and usage guides

### Technical Details
- Pyro4 for remote procedure calls
- Asynchronous task distribution
- In-memory data management
- Fault detection and recovery mechanisms

## Project History
- Original Name: map-reduce
- Created: 2022
- Type: Educational Project (Distributed Systems)
- Contributors:
  - Ricardo Piloto (@cassius66)
  - Carlos Luis Águila Fajardo (@kvothe9991)
- Reformatted: February 2025 using CLINE Assistant
