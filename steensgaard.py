"""
Program to Implement Steensgaard's Points-to Analysis in Almost Linear Time

Course: COS 516
Authors: Tanvi Namjoshi & Lana Glisic
"""

import networkx as nx
import matplotlib.pyplot as plt
import argparse
import sys
import actions
from sil_parser import *
from type import TypeManager


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

    parser = argparse.ArgumentParser(
        description="A python implementation of Steensgaard's Points-to Analysis."
    )

    # Command line arguments
    parser.add_argument(
        "-fn", "--filename", type=str, help="Specify a filename for a SIL program."
    )

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

            # Manage type nodes
            manager = TypeManager()

            # Map variable names to type nodes
            map = {}

            for c in constraints:
                # Find Type node of LHS variable
                x = map.get(c["lhs"])

                # Instantiate Type if LHS variable is new
                if x is None:
                    x = manager.new_alpha()
                    map[c["lhs"]] = x

                # Accommodate operations with no RHS variable
                y = None

                # Find type node of RHS variable
                if "rhs" in c:
                    y = map.get(c["rhs"])

                    # Instantiate Type node if RHS variable is new
                    if y is None:
                        y = manager.new_alpha()
                        map[c["rhs"]] = y

                match c["type"]:
                    case "assign":
                        print("assign", c["lhs"], c["rhs"])
                        actions.constraint_assign(manager, x, y)
                    case "addr_of":
                        print("addr_of", c["lhs"], c["rhs"])
                        actions.constraint_addr_of(manager, x, y)
                    case "deref":
                        print("deref", c["lhs"], c["rhs"])
                        actions.constraint_deref(manager, x, y)
                    case "store":
                        print("store", c["lhs"], c["rhs"])
                        actions.constraint_store(manager, x, y)
                    case _:
                        print("Unrecognized constraint.")
                print(manager.uf)
                print(map)
                for key, node in map.items():
                    print(key, node.uf_id, node.tau_ref, "<--")
            return 0
    else:
        print("No filename provided.")
        return -1


if __name__ == "__main__":
    # Call the main function with command-line arguments
    sys.exit(main(sys.argv[1:]))
