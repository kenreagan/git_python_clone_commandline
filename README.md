# Distributed Source Control System

## Overview

This project is a lightweight, Python-based source control system inspired by Git, providing core version control functionality with a focus on simplicity and educational value.

## Features

### Core Functionality
- Repository Initialization
- File Staging
- Commit Management
- Branch Management
- Diff Tracking
- File History
- Commit Restoration

### Supported Operations
- Create and switch branches
- Stage individual files
- Commit changes with messages
- Compare files and commits
- Restore previous file versions

## Project Structure

```
source-control-system_python/
├── src/
│   ├── core/                  # Core system components
│   │   ├── repository.py      # Repository initialization
│   │   ├── staging.py         # File staging
│   │   ├── commit.py          # Commit management
│   │   ├── history.py         # Commit history tracking
│   │   ├── branch.py          # Branch management
│   │   ├── merge.py           # Branch merging
│   │   ├── diff.py            # Diff generation
│   │   └── ignore.py          # Ignored file handling
│   ├── cli.py                 # Command-line interface
│   └── utils.py               # Utility functions
├── tests/                     # Unit tests
|   └── __init__.py 
|   └── test_branch.py
|   └── test_diff.py
|   └── test_commit.py
└── pyproject.toml             # Project configuration
```

## Installation

### Requirements
- Python 3.9+
- Poetry (recommended for dependency management)

### Setup
1. Clone the repository
2. Install dependencies:
   ```bash
   poetry install
   ```

## Usage

### Initialize a Repository
```bash
python -m src.cli init /path/to/repository
```

### Basic Workflow
```bash
# Stage files
python -m src.cli add file1.txt file2.txt

# Commit changes
python -m src.cli commit -m "Initial commit"

# Create a new branch
python -m src.cli branch feature-new

# Switch branches
python -m src.cli checkout feature-new

# View commit history
python -m src.cli log
```

## Design Philosophy

This source control system is designed to:
- Provide a clear, educational implementation of version control concepts
- Demonstrate core Git-like functionality
- Serve as a learning resource for understanding distributed version control

## Limitations

Current implementation does not support:
- Network-based operations
- Advanced merge conflict resolution
- Extensive branching strategies
- Large file handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request


## Authors

Lumuli Ken Reagan
email: (lumulikenreagan@gmail.com)

## Acknowledgments

Inspired by Git and designed as an educational project to demonstrate version control system internals.