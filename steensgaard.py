"""
Program to Implement Steensgaard's Points-to Analysis in Almost Linear Time

Course: COS 516
Authors: Tanvi Namjoshi & Lana Glisic
"""

import networkx as nx
import matplotlib.pyplot as plt
import argparse
import sys
from sil_parser import *
from analyst import *
import time


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


def create_graph(uf, map):
    # TODO Tanvi add comments + clean up code
    G = nx.DiGraph()
    sets = uf.get_sets()
    print("SETS:", tuple(sets))

    for set in sets:
        for node in set:
            G.add_node(tuple(set))
    for key, node in map.items():
        if node.tau is None:
            continue
        else:
            # Find the set that contains node.uf_id for start and end
            start = "start"
            end = "end"
            end_node = node.tau
            for set in sets:
                if end_node in set:
                    end = tuple(set)
                if node.uf_id in set:
                    start = tuple(set)
            G.add_edge(start, end)
    print("Start drawing")
    pos = nx.planar_layout(G)
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color="lightblue",
        font_weight="bold",
        node_size=1000,
    )
    plt.title("Storage Shape Graph for SIL Program")
    # plt.show()
    # nx.draw(G, with_labels=True, font_weight="bold")
    plt.show()
    return G


def get_typing(variables, analyst):
    for variable in variables:
        ecr_v = analyst.ecr(variable)
        type_var = analyst.nodes[ecr_v]
        print(f"Variable {variable} (ECR {ecr_v}): TypeNode {type_var}")


def run_steensgaard_analysis(variables, constraints):
    # variables is a set of variable names in the program
    # constraints is a list of constraints parsed from the SIL program

    analyst = Analyst()

    # Initialize Type nodes for all variables
    for v in variables:
        analyst.new_type(v)

    for c in constraints:
        print("Processing constraint:", c)

        match c["type"]:
            case "assign":
                print("assign", c["lhs"], c["rhs"])
                analyst.handle_assign(c["lhs"], c["rhs"])
            case "addr_of":
                print("addr_of", c["lhs"], c["rhs"])
                analyst.handle_addr_of(c["lhs"], c["rhs"])
            case "deref":
                print("deref", c["lhs"], c["rhs"])
                analyst.handle_deref(c["lhs"], c["rhs"])
            case "op":
                print("op", c["lhs"], c["operands"])
                analyst.handle_op(c["lhs"], c["operand_variables"])
            case "allocate":
                print("allocate", c["lhs"])
                analyst.handle_allocate(c["lhs"])
            case _:
                print("Unrecognized constraint.")

        print("Pending:", analyst.pending)
        get_typing(variables, analyst)

    print("Final Types:")
    get_typing(variables, analyst)

    return analyst.uf, analyst.nodes


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
            print("List of all constraints:")
            print(constraints)
            n = len(constraints)  # number of constraints
            print(f"Total number of constraints: {n}")
            all_variables = get_all_variables(ast)
            print(f"\nAll variable names encountered: {sorted(all_variables)}")
            print("Parsing completed.")

            # Run Steensgaard's analysis, and time it (for performance measurement)
            start_time = time.perf_counter()
            uf, nodes = run_steensgaard_analysis(all_variables, constraints)
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
            print(
                f"\nSteensgaard's analysis on {n} constraints completed in {elapsed_time:.6f} seconds."
            )
            G = create_graph(uf, nodes)
            return 0
    else:
        print("No filename provided.")
        return -1


if __name__ == "__main__":
    # Call the main function with command-line arguments
    sys.exit(main(sys.argv[1:]))
