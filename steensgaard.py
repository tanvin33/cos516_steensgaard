'''
Program to Implement Steensgaard's Points-to Analysis in Almost Linear Time

Course: COS 516
Authors: Tanvi Namjoshi & Lana Glisic
'''

import networkx as nx
import matplotlib.pyplot as plt
import argparse
import sys
from pyparser import *

def parse_program(program: str):
    """
    Parses the inputted SIL program and returns its AST.
    Args:
        program (str): The SIL program as a string.
    Returns:
        ast (list): The Abstract Syntax Tree (AST) of the program.
        constraints (list): The list of constraints extracted from the AST.
    """
    parser = create_sil_parser()
    try:
        ast = parser.parse_string(program)
        constraints = get_all_constraints(ast)
        return ast, constraints
    except pp.ParseException as e:
      print("Parse Error:", e)

def main(args=None):
    """
    The main entry point to start the analysis.
    Takes in command-line arguments for the filename of a SIL program.
    Returns the completed analysis.
    """

    parser = argparse.ArgumentParser(description="A python implementation of Steensgaard's Points-to Analysis.")

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
            ast, constraints = parse_program(program)
            print("ALL CONSTRAINTS:")
            print(constraints)
            print("Parsing completed.")
            return 0
    else:
        print("No filename provided.")
        return -1

if __name__ == "__main__":
    # Call the main function with command-line arguments
    sys.exit(main(sys.argv[1:]))
