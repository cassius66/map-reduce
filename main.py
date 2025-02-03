#!/usr/bin/env python3
"""
Main entry point for the MapReduce system.
Handles both server and client initialization.
"""
from __future__ import annotations

import argparse
import logging
import signal
import sys
from time import sleep
from typing import Dict, Optional

import Pyro4
import Pyro4.errors
import Pyro4.naming
import Pyro4.socketutil
import Pyro4.util
from Pyro4 import Daemon, URI

from map_reduce.client.client import run_client
from map_reduce.server.configs import (BROADCAST_PORT, DAEMON_PORT, DHT_NAME,
                                     FOLLOWER_NAME, IP, MASTER_NAME,
                                     RQ_HANDLER_NAME)
from map_reduce.server.dht import ChordNode, ChordService, service_address
from map_reduce.server.logger import get_logger
from map_reduce.server.nameserver import NameServer
from map_reduce.server.nodes import Follower, Master, RequestHandler

# Configure Pyro4
Pyro4.config.SERVERTYPE = 'thread'
Pyro4.config.SERIALIZER = 'dill'
Pyro4.config.SERIALIZERS_ACCEPTED.add('dill')

logger = get_logger('main')
logger = logging.LoggerAdapter(logger, {'IP': IP})

class MapReduceServer:
    """Main server class that manages all components of the MapReduce system."""
    
    def __init__(self) -> None:
        self.daemon: Optional[Daemon] = None
        self.nameserver: Optional[NameServer] = None
        self.dht: Optional[ChordNode] = None
        self.dht_service: Optional[ChordService] = None
        self.running: bool = False
        
        # Setup addresses
        self.dht_address = URI(f'PYRO:{DHT_NAME}@{IP}:{DAEMON_PORT}')
        self.dht_service_address = service_address(self.dht_address)
        self.master_address = URI(f'PYRO:{MASTER_NAME}@{IP}:{DAEMON_PORT}')
        self.follower_address = URI(f'PYRO:{FOLLOWER_NAME}@{IP}:{DAEMON_PORT}')
        self.rqh_address = URI(f'PYRO:{RQ_HANDLER_NAME}@{IP}:{DAEMON_PORT}')

    def setup_daemon(self, objects: Dict) -> None:
        """Setup main daemon with the provided objects."""
        self.daemon = Pyro4.Daemon(host=IP, port=DAEMON_PORT)
        for name, obj in objects.items():
            self.daemon.register(obj, name)

    def setup_nameserver(self) -> None:
        """Setup and configure the nameserver."""
        self.nameserver = NameServer(IP, BROADCAST_PORT)
        self.nameserver.delegate(
            self.rqh_address, 
            self.request_handler.start, 
            self.request_handler.stop
        )
        self.nameserver.delegate(
            self.master_address,
            self.master.start,
            self.master.stop
        )
        self.nameserver.start()

    def signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals gracefully."""
        logger.info(f'Received signal {signum}')
        self.shutdown()

    def shutdown(self) -> None:
        """Gracefully shutdown all components."""
        self.running = False
        
        if self.nameserver:
            logger.info('Stopping nameserver...')
            self.nameserver.stop()
        
        if self.daemon:
            logger.info('Stopping main daemon...')
            self.daemon.shutdown()
        
        # Cleanup resources
        self.dht = None
        self.dht_service = None
        logger.info('Server shutdown complete.')
        sys.exit(0)

    def run(self) -> None:
        """Run the MapReduce server."""
        # Initialize components
        self.dht = ChordNode(self.dht_address)
        self.dht_service = ChordService(self.dht_service_address, self.dht_address)
        self.master = Master(self.master_address)
        self.follower = Follower(self.follower_address)
        self.request_handler = RequestHandler(self.rqh_address)

        # Setup daemon with all objects
        self.setup_daemon({
            self.dht_address.object: self.dht,
            self.dht_service_address.object: self.dht_service,
            MASTER_NAME: self.master,
            FOLLOWER_NAME: self.follower,
            RQ_HANDLER_NAME: self.request_handler
        })

        # Setup nameserver
        self.setup_nameserver()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Wait for nameservers to stabilize
        logger.info('Waiting for nameserver initialization...')
        sleep(5)
        
        # Start main request loop
        self.running = True
        logger.info('Server started successfully')
        try:
            while self.running and self.daemon:
                self.daemon.requestLoop(timeout=1.0)
        except Exception as e:
            logger.error(f'Error in main loop: {e}')
            self.shutdown()

def main() -> None:
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description='Start a MapReduce module.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'module',
        choices=['server', 'client'],
        help='Module to run (server or client)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.module == 'server':
            server = MapReduceServer()
            server.run()
        else:
            run_client()
    except Exception as e:
        logger.error(f'Fatal error: {e}')
        sys.exit(1)

if __name__ == "__main__":
    main()
