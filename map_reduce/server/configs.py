import logging
import Pyro4.socketutil

# Exceptions.
class ConfigError(Exception):
    pass

# General.
IP = Pyro4.socketutil.getIpAddress(None, workaround127=None)
DAEMON_PORT = 8008
BROADCAST_PORT = 8009
REQUEST_TIMEOUT = 0.5  # Seconds - increased from 0.02 for better stability
REQUEST_RETRIES = 5
MAX_TASK_TIMEOUT = 300  # 5 minutes timeout for tasks
RESULTS_KEY = 'map-reduce/final-results'

# DHT.
DHT_NAME = 'chord.dht'
DHT_SERVICE_NAME = 'chord.dht.service'
DHT_FINGER_TABLE_SIZE = 160 // 2
DHT_STABILIZATION_INTERVAL = 1.0  # Increased from 0.1 to reduce network load
DHT_RECHECK_INTERVAL = 1
DHT_REPLICATION_SIZE = 5

# NS.
NS_CONTEST_INTERVAL = 0.01
NS_BACKUP_INTERVAL = 5
NS_BACKUP_KEY = 'ns/backup'

# Master.
MASTER_NAME = 'master'
MASTER_DATA = 'master/staged/data'
MASTER_MAP_CODE = 'master/staged/map-code'
MASTER_REDUCE_CODE = 'master/staged/reduce-code'
MASTER_BACKUP_KEY = 'master/backup'
MASTER_BACKUP_INTERVAL = 2
ITEMS_PER_CHUNK = 16

# Follower.
FOLLOWER_NAME = 'follower'

# Request handler.
RQ_HANDLER_NAME = 'rq.handler'


# Logging.
LOGGING = {
    'main': {
        'color': '\033[1;34m',  # Blue.
        'level': logging.INFO,
    },
    'dht': {
        'color': '\x1b[33;20m', # Yellow.
        'level': logging.INFO,
    },
    'dht:s': {
        'color': '\x1b[33;20m', # Yellow.
        'level': logging.INFO,
    },
    'ns': {
        'color': '\033[1;32m',  # Green.
        'level': logging.INFO,
    },
    'flwr': {
        'color': '\x1b[1;31m',  # Red.
        'level': logging.DEBUG,
    },
    'mstr': {
        'color': '\x1b[1;31m',  # Red.
        'level': logging.INFO,
    },
    'test': {
        'color': '\x1b[1;31m',  # Red.
        'level': logging.DEBUG,
    },
    'lock': {
        'color': '\x1b[1;31m',  # Red.
        'level': logging.DEBUG,
    }
}
