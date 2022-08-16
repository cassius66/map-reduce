import select
import socket
import logging
import threading
from time import sleep

import Pyro4
import Pyro4.errors
import Pyro4.naming
import Pyro4.socketutil
from Pyro4 import Proxy, URI

Pyro4.config.SERVERTYPE = 'thread'
# Pyro4.config.SERVERTYPE = 'multiplex'
# Pyro4.config.COMMTIMEOUT = 3

from map_reduce.server.configs import *
from map_reduce.server.dht import ChordNode, ChordService, service_address
from map_reduce.server.logger import get_logger
from map_reduce.server.nameserver import NameServer

HOST = socket.gethostname()
IP = Pyro4.socketutil.getIpAddress(None, workaround127=None)
DHT_ADDRESS = URI(f'PYRO:{DHT_NAME}@{IP}:{DAEMON_PORT}')
DHT_SERVICE_ADDRESS = service_address(DHT_ADDRESS)


logger = get_logger('main')
logger = logging.LoggerAdapter(logger, {'IP': IP})

def setup_daemon(ip: str, port: int, objects: dict):
    ''' Setup main daemon. '''
    daemon = Pyro4.Daemon(host=ip, port=port)
    for name, obj in objects.items():
        daemon.register(obj, name)
    return daemon

def setup_nameserver(ip: str, port: int):
    ''' Setup the nameserver wrapper. '''
    return NameServer(ip, port)

def handle_requests(main_daemon: Pyro4.Daemon, ns: NameServer):
    '''
    Forward requests for the nameserver, its broadcast server, and our custom Daemon.
    Implicitly lets nameserver bindings autorefresh, and waits a certain time to cache
    requests.
    '''
    ns_daemon, ns_broadcast = ns.servers

    # Join all sockets for request processing.
    sockets = main_daemon.sockets
    if ns.is_local:
        sockets.extend(ns_daemon.sockets)
        sockets.append(ns_broadcast)

    # Wait for a request.
    rqs, *_ = select.select(sockets, [], [], REQUESTS_WAIT_TIME)

    # Forward requested sockets to the owner daemon.
    events_for_ns = []
    events_for_main = []
    for rq in rqs:
        if rq is ns_broadcast:
            ns_broadcast.processRequest()
        elif rq in ns_daemon.sockets:
            events_for_ns.append(rq)
        elif rq in main_daemon.sockets:
            events_for_main.append(rq)
    
    # Process requests.
    if events_for_ns:
        ns_daemon.events(events_for_ns)
    if events_for_main:
        main_daemon.events(events_for_main) 

def request_loop(main_daemon: Pyro4.Daemon, ns: NameServer):
    '''
    High level loop that multiplexes requests to the nameserver and the main daemon.
    '''
    while True:
        ns.refresh_nameserver()
        handle_requests(main_daemon, ns)

if __name__ == "__main__":

    # Main daemon.
    objs_for_daemon = {}

    dht = ChordNode(DHT_ADDRESS)
    objs_for_daemon[DHT_ADDRESS.object] = dht

    dht_service = ChordService(DHT_SERVICE_ADDRESS, DHT_ADDRESS)
    objs_for_daemon[DHT_SERVICE_ADDRESS.object] = dht_service

    main_daemon = setup_daemon(IP, DAEMON_PORT, objs_for_daemon)

    # Nameserver.
    nameserver = setup_nameserver(IP, BROADCAST_PORT)
    nameserver.start()
    sleep(5)

    # DHT setup.
    with Pyro4.locateNS() as ns:
        try:
            ring_addr = ns.lookup(DHT_NAME)
            dht.join(ring_addr)
        except Pyro4.errors.NamingError:
            logger.info(f'No DHT found. Registering {DHT_NAME} at nameserver {ns._pyroUri}.')
            ns.register(DHT_NAME, DHT_ADDRESS)
    
    # Start request loop.
    try:
        main_daemon.requestLoop()
    except KeyboardInterrupt:
        logger.info('Server stopped by user.')
    finally:
        logger.info('Killing nameserver.')
        nameserver.stop()
        
        logger.info('Killing main daemon.')
        main_daemon.shutdown()
        
        del nameserver
        del main_daemon
        del dht
        del dht_service

        logger.info('Exiting.')
        exit(0)