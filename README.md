# map-reduce

A distributed MapReduce implementation in Python: a Chord distributed hash
table underneath, Pyro4 for remote calls, and master and follower nodes that
survive each other's failure.

## Why

Distributed Systems coursework, 2022, written with
[@kvothe9991](https://github.com/kvothe9991). MapReduce is easy to describe and
hard to build, because the interesting part is not the map or the reduce, it is
what happens when a node disappears halfway through a task. This implementation
puts the work on a Chord ring so that node membership can change while a job is
running, and elects a new master when the old one stops answering.

## Setup

```bash
pip install -r requirements.txt

scripts/run_container      # start a node in Docker
scripts/batch_run          # start several
scripts/run_client         # submit a job
scripts/batch_tail         # follow the logs
scripts/batch_kill         # stop everything
scripts/test               # run the tests
```

A job is a Python file defining a map and a reduce function.
`examples/word_count.py` over `examples/sample.txt` is the worked example.
Functions are serialized with `dill` and shipped to the followers, so a job
does not have to exist on the nodes beforehand.

## Structure

```text
main.py                          entry point for a node
Dockerfile                       the node image
requirements.txt                 Pyro4, dill
map_reduce/
├── client/
│   ├── client.py                submits a job and collects results
│   └── server_interface.py      the client's view of the cluster
├── server/
│   ├── configs.py               addresses, ports, timeouts
│   ├── logger.py                per-node logging
│   ├── utils.py                 shared helpers
│   ├── dht/
│   │   ├── chord.py             the Chord ring: finger table, stabilization
│   │   └── data_layer.py        what the ring stores and how it is keyed
│   ├── nameserver/
│   │   └── nameserver.py        Pyro4 name resolution, with failover
│   └── nodes/
│       ├── master.py            partitions the job, assigns and tracks tasks
│       ├── follower.py          runs map and reduce tasks
│       ├── request_handler.py   accepts client requests, notifies the master
│       ├── tasks.py             the task model and its states
│       └── threader_node.py     the threading base both node types share
└── tests/
    ├── dht.py                   Chord ring behavior
    └── nameserver.py            name resolution and failover
scripts/                         run, batch, tail, kill, test
examples/                        word_count.py over sample.txt
```

## Stack

Python, Pyro4 for remote procedure calls, `dill` for shipping functions to
nodes, Docker for running a cluster on one machine.

## Not Done

- **In-memory only.** The data layer does not persist. Restarting the ring
  loses what it held.
- **No result checkpointing.** A job that loses its master mid-run is
  re-assigned, not resumed.
- **Tests cover the DHT and the nameserver**, not the end-to-end job path.
- **`map_reduce/client/data.txt` is committed test input**, not a fixture the
  examples use.

## Status

Dormant. Written in 2022, last worked on 2025-02. It runs, and nobody is
working on it.

This repo carries commits that the upstream at
[kvothe9991/map-reduce](https://github.com/kvothe9991/map-reduce) does not.

## License

The Unlicense. Public domain.
