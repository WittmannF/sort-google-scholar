#!/usr/bin/env python3

import os

# List of keywords extracted from existing CSV files
keywords = [
    "Deep Learning",
    "Machine Learning",
    "Neural Networks",
    "Non Intrusive Load Monitoring",
]

# Path to examples directory
examples_dir = os.path.dirname(os.path.abspath(__file__))

print("Updating example files...")
for search_kw in keywords:
    # Format command: run sortgs with the keyword and save CSV to examples directory
    cmd = f'sortgs "{search_kw}"'

    print(f"Running: {cmd}")
    os.system(cmd)

print("All examples updated successfully!")
