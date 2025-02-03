#!/usr/bin/env python3
"""
Word Count Example using MapReduce Framework
This example demonstrates how to use the MapReduce framework to count word occurrences
in a text file or a list of strings.
"""

from map_reduce.client.server_interface import ServerInterface
from typing import List, Tuple
import argparse
import os

def map_function(line_num: int, line: str) -> List[Tuple[str, int]]:
    """
    Map function that splits each line into words and emits (word, 1) pairs.
    
    Args:
        line_num: Line number in the input text
        line: The text line to process
    
    Returns:
        List of tuples containing (word, 1) pairs
    """
    # Split line into words and emit (word, 1) for each word
    return [(word.lower(), 1) for word in line.split()]

def reduce_function(word: str, counts: List[int]) -> int:
    """
    Reduce function that sums up all counts for each word.
    
    Args:
        word: The word being counted
        counts: List of counts for this word from different map tasks
    
    Returns:
        Total count for the word
    """
    return sum(counts)

def process_file(filepath: str) -> None:
    """
    Process a text file using MapReduce to count word occurrences.
    
    Args:
        filepath: Path to the text file to process
    """
    # Read input data
    try:
        with open(filepath, 'r') as f:
            data = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found")
        return
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return

    # Initialize server interface
    server = ServerInterface()
    
    # Start MapReduce processing
    print(f"Processing file: {filepath}")
    print(f"Total lines to process: {len(data)}")
    
    if daemon := server.startup(data, map_function, reduce_function):
        print("MapReduce tasks started, processing...")
        results = server.await_results()
        
        # Print results
        print("\nWord Count Results:")
        print("-" * 40)
        # Sort by count in descending order
        sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        for word, count in sorted_results:
            print(f"{word}: {count}")
        print("-" * 40)
        print(f"Total unique words: {len(results)}")
    else:
        print("Failed to start MapReduce daemon")

def main():
    # Example text if no file is provided
    example_text = [
        "Hello MapReduce World",
        "This is a MapReduce example",
        "MapReduce is powerful and distributed",
        "Hello again distributed world"
    ]
    
    parser = argparse.ArgumentParser(description='Word Count using MapReduce')
    parser.add_argument('--file', '-f', help='Input text file to process')
    args = parser.parse_args()
    
    if args.file:
        process_file(args.file)
    else:
        print("Using example text (use --file to specify an input file)")
        server = ServerInterface()
        if daemon := server.startup(example_text, map_function, reduce_function):
            print("Processing example text...")
            results = server.await_results()
            
            print("\nWord Count Results:")
            print("-" * 40)
            sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
            for word, count in sorted_results:
                print(f"{word}: {count}")
            print("-" * 40)
            print(f"Total unique words: {len(results)}")

if __name__ == "__main__":
    main()
