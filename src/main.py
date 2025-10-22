#!/usr/bin/env python3
"""SQL Query Optimizer - Main Entry Point.

This is the main entry point for the SQL Query Optimizer application.
It provides a command-line interface for optimizing SQL queries using
LLM technology for various database systems.

Usage:
    python main.py optimize query.sql --database oracle
    python main.py compare query.sql --databases oracle,sqlite
    python main.py list-databases
    python main.py list-providers

For more information, run:
    python main.py --help
"""

from presentation.cli.commands import main

if __name__ == "__main__":
	main()
