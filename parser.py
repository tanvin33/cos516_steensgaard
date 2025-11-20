# Steps 
# 1. Break up program into commands (lines ending with ;)
# 2. Parse each command according to the grammar above

import argparse
import sys
import re
from typing import List, Union


def process(program: str):
  """
  Processes the inputted SIL program and parses it according to the defined grammar.
  Args:
      program (str): The SIL program as a string.
  """
  # First check that the program does not end on ';'
  if program.strip().endswith(';'):
      raise ValueError("Program should not end with a semicolon ';'.")
  else:
      print("Program format looks good.")

  # Split the program into commands based on semicolons
  commands = [cmd.strip() for cmd in program.split(';') if cmd.strip()]

  for command in commands:
      print(f"Processing command: {command}")
      if command.startswith("skip"):
          print("Parsed a skip command.")
      elif command.startswith("if"):
          print("Parsed an if statement.")
      elif command.startswith("while"):
          print("Parsed a while loop.")
      elif ":=" in command:
          print("Parsed an assignment.")
      else:
          print("Unknown command format.")

      # Here you would add the parsing logic according to the grammar
      # For demonstration, we will just print the command

def main(args=None):
    """
    The main function of the script.
    Processes the inputted SIL program and parses it according to the defined grammar.
    """

    parser = argparse.ArgumentParser(description="A simple imperative language parser.")

    # Command line arguments
    parser.add_argument("-fn", "--filename", type=str, 
                        help="Specify a filename for a SIL program.")
  

    # Parse the arguments
    # If args is None, parse_args will default to sys.argv[1:]
    program_fn = parser.parse_args(args).filename

    # Access the parsed arguments
    if program_fn:
        with open(program_fn, "r") as f:
            program = f.read()
            print(program)
            process(program)
            print("Parsing completed.")
            return 0
    else:
        print("No filename provided.")
        return 1

if __name__ == "__main__":
    # Call the main function with command-line arguments
    sys.exit(main(sys.argv[1:]))
