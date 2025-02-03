"""
Configuration management for the MapReduce framework.
Handles all system-wide settings and provides validation.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, Optional

import Pyro4.socketutil
from typing_extensions import TypedDict

class ConfigError(Exception):
    """Raised when configuration validation fails."""
    pass

class LogConfig(TypedDict):
    """Type definition for logging configuration."""
    level: str
    json_format: bool
    log_file: Optional[str]

@dataclass
class NetworkConfig:
    """Network-related configuration."""
    ip: str = Pyro4.socketutil.getIpAddress(None, workaround127=None)
    daemon_port: int = int(os.getenv('MR_DAEMON_PORT', '8008'))
    broadcast_port: int = int(os.getenv('MR_BROADCAST_PORT', '8009'))
    request_timeout: float = float(os.getenv('MR_REQUEST_TIMEOUT', '0.5'))
    request_retries: int = int(os.getenv('MR_REQUEST_RETRIES', '5'))

    def validate(self) -> None:
        """Validate network configuration."""
        if self.daemon_port < 1024 or self.daemon_port > 65535:
            raise ConfigError(f"Invalid daemon port: {self.daemon_port}")
        if self.broadcast_port < 1024 or self.broadcast_port > 65535:
            raise ConfigError(f"Invalid broadcast port: {self.broadcast_port}")
        if self.request_timeout <= 0:
            raise ConfigError(f"Invalid request timeout: {self.request_timeout}")
        if self.request_retries < 1:
            raise ConfigError(f"Invalid request retries: {self.request_retries}")

@dataclass
class DHTConfig:
    """DHT (Distributed Hash Table) configuration."""
    name: str = 'chord.dht'
    service_name: str = 'chord.dht.service'
    finger_table_size: int = 160 // 2
    stabilization_interval: float = float(os.getenv('MR_DHT_STABILIZATION_INTERVAL', '1.0'))
    recheck_interval: float = float(os.getenv('MR_DHT_RECHECK_INTERVAL', '1.0'))
    replication_size: int = int(os.getenv('MR_DHT_REPLICATION_SIZE', '5'))

    def validate(self) -> None:
        """Validate DHT configuration."""
        if self.finger_table_size < 1:
            raise ConfigError(f"Invalid finger table size: {self.finger_table_size}")
        if self.stabilization_interval <= 0:
            raise ConfigError(f"Invalid stabilization interval: {self.stabilization_interval}")
        if self.replication_size < 1:
            raise ConfigError(f"Invalid replication size: {self.replication_size}")

@dataclass
class TaskConfig:
    """Task execution configuration."""
    max_timeout: int = int(os.getenv('MR_MAX_TASK_TIMEOUT', '300'))  # 5 minutes
    items_per_chunk: int = int(os.getenv('MR_ITEMS_PER_CHUNK', '16'))
    results_key: str = 'map-reduce/final-results'

    def validate(self) -> None:
        """Validate task configuration."""
        if self.max_timeout < 1:
            raise ConfigError(f"Invalid max task timeout: {self.max_timeout}")
        if self.items_per_chunk < 1:
            raise ConfigError(f"Invalid items per chunk: {self.items_per_chunk}")

@dataclass
class NameServerConfig:
    """Nameserver configuration."""
    contest_interval: float = float(os.getenv('MR_NS_CONTEST_INTERVAL', '0.01'))
    backup_interval: float = float(os.getenv('MR_NS_BACKUP_INTERVAL', '5.0'))
    backup_key: str = 'ns/backup'

    def validate(self) -> None:
        """Validate nameserver configuration."""
        if self.contest_interval <= 0:
            raise ConfigError(f"Invalid contest interval: {self.contest_interval}")
        if self.backup_interval <= 0:
            raise ConfigError(f"Invalid backup interval: {self.backup_interval}")

@dataclass
class NodeConfig:
    """Node configuration for master and follower nodes."""
    master_name: str = 'master'
    follower_name: str = 'follower'
    request_handler_name: str = 'rq.handler'
    master_data: str = 'master/staged/data'
    master_map_code: str = 'master/staged/map-code'
    master_reduce_code: str = 'master/staged/reduce-code'
    master_backup_key: str = 'master/backup'
    master_backup_interval: float = float(os.getenv('MR_MASTER_BACKUP_INTERVAL', '2.0'))

    def validate(self) -> None:
        """Validate node configuration."""
        if self.master_backup_interval <= 0:
            raise ConfigError(f"Invalid master backup interval: {self.master_backup_interval}")

# Default logging configuration
LOGGING: Dict[str, LogConfig] = {
    'main': {
        'level': 'INFO',
        'json_format': True,
        'log_file': 'logs/main.log'
    },
    'dht': {
        'level': 'INFO',
        'json_format': True,
        'log_file': 'logs/dht.log'
    },
    'ns': {
        'level': 'INFO',
        'json_format': True,
        'log_file': 'logs/nameserver.log'
    },
    'follower': {
        'level': 'DEBUG',
        'json_format': False,
        'log_file': None
    },
    'master': {
        'level': 'INFO',
        'json_format': True,
        'log_file': 'logs/master.log'
    },
    'test': {
        'level': 'DEBUG',
        'json_format': False,
        'log_file': None
    }
}

# Create and validate configuration instances
try:
    network = NetworkConfig()
    network.validate()

    dht = DHTConfig()
    dht.validate()

    task = TaskConfig()
    task.validate()

    nameserver = NameServerConfig()
    nameserver.validate()

    node = NodeConfig()
    node.validate()

except ValueError as e:
    raise ConfigError(f"Configuration error: {str(e)}")

# Export commonly used values as module-level constants
IP = network.ip
DAEMON_PORT = network.daemon_port
BROADCAST_PORT = network.broadcast_port
REQUEST_TIMEOUT = network.request_timeout
REQUEST_RETRIES = network.request_retries

DHT_NAME = dht.name
DHT_SERVICE_NAME = dht.service_name
DHT_FINGER_TABLE_SIZE = dht.finger_table_size
DHT_STABILIZATION_INTERVAL = dht.stabilization_interval
DHT_RECHECK_INTERVAL = dht.recheck_interval
DHT_REPLICATION_SIZE = dht.replication_size

MAX_TASK_TIMEOUT = task.max_timeout
ITEMS_PER_CHUNK = task.items_per_chunk
RESULTS_KEY = task.results_key

NS_CONTEST_INTERVAL = nameserver.contest_interval
NS_BACKUP_INTERVAL = nameserver.backup_interval
NS_BACKUP_KEY = nameserver.backup_key

MASTER_NAME = node.master_name
FOLLOWER_NAME = node.follower_name
RQ_HANDLER_NAME = node.request_handler_name
MASTER_DATA = node.master_data
MASTER_MAP_CODE = node.master_map_code
MASTER_REDUCE_CODE = node.master_reduce_code
MASTER_BACKUP_KEY = node.master_backup_key
MASTER_BACKUP_INTERVAL = node.master_backup_interval
