from pprint import pp
from map_reduce.client.server_interface import ServerInterface as server

import os
from typing import Any, Callable, List, Tuple, TypeVar

K = TypeVar('K')
V = TypeVar('V')

def validate_map_function(func: Callable) -> bool:
    """Validate that map function follows required schema"""
    try:
        result = func(0, "test string")
        if not isinstance(result, list):
            raise ValueError("Map function must return a list")
        if result and not isinstance(result[0], tuple):
            raise ValueError("Map function must return list of tuples")
        return True
    except Exception as e:
        print(f"Invalid map function: {str(e)}")
        return False

def validate_reduce_function(func: Callable) -> bool:
    """Validate that reduce function follows required schema"""
    try:
        result = func("test", [1, 2, 3])
        return True
    except Exception as e:
        print(f"Invalid reduce function: {str(e)}")
        return False

def map(doc_line: int, doc_line_text: str) -> List[Tuple[str, int]]:
    """Map function that splits text into words and counts them"""
    res = []
    for word in doc_line_text.split():
        res.append((word, 1))
    return res

def reduce(word: str, vals: List[int]) -> int:
    """Reduce function that sums up word counts"""
    return sum(vals)

def run_client(data_file: str = 'map_reduce/client/data.txt'):
    """Run the MapReduce client with configurable data file"""
    try:
        # Validate data file exists
        if not os.path.exists(data_file):
            raise FileNotFoundError(f"Data file not found: {data_file}")
            
        # Read data
        with open(data_file) as file:
            data = [line.strip() for line in file.readlines()]
            
        # Validate functions
        if not validate_map_function(map) or not validate_reduce_function(reduce):
            raise ValueError("Invalid map/reduce functions")
            
        # Start processing
        if daemon := server.startup(data, map, reduce):
            print('MapReduce tasks started, awaiting results...')
            server.await_results()
            pp(server.results, indent=4, sort_dicts=True)
        else:
            print("Failed to start MapReduce daemon")
    except Exception as e:
        print(f"Error running MapReduce client: {str(e)}")
