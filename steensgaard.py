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
import pandas as pd
import math


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
    # Create a new networkx directed graph
    G = nx.DiGraph()
    sets = uf.get_sets()  # get the ECR sets
    for set in sets:
        G.add_node(
            tuple(set)
        )  # each set is a node in the graph (named after all its members)
    for key, node in map.items():
        if node.tau is None:
            continue  # skip if tau is None (no points-to relation)
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
            G.add_edge(start, end)  # add directed edge from start to end

    return G


def draw_single_graph(filename, uf, map):
    G = create_graph(uf, map)
    # Draw the graph
    plt.figure()
    plt.title(f"Storage Shape Graph for SIL Program: {filename}")

    pos = nx.planar_layout(G)
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color="lightblue",
        font_weight="bold",
        node_size=1000,
        arrowsize=25,
    )
    plt.savefig(f"{filename}_graph.png")  # Save the graph as a PNG file
    plt.show()  # Show the graph, needs to be closed manually for program to continue
    return G


def get_debugging_types(variables, analyst):
    """
    This function prints the current typing of all variables for debugging.
    It prints out the variable name, its ECR (representative), and its associated
    TypeNode.

    """
    for variable in sorted(variables):  # sort the variables:
        ecr_v = analyst.ecr(variable)
        type_var = analyst.nodes[ecr_v]
        print(f"Variable {variable} (ECR {ecr_v}): TypeNode {type_var}")


def get_typing(variables, analyst):
    """
    This function prints the final typing of all variables.
    Args:
        variables (set): Set of variable names in the program.
        analyst (Analyst): The Analyst object containing the analysis results.
    """
    for variable in sorted(variables):  # sort the variables:
        ecr_v = analyst.ecr(variable)
        type_var = analyst.nodes[ecr_v]
        type_tau = analyst.ecr(type_var.tau) if type_var.tau != None else "\u22a5"
        type_lambda = type_var.lam if type_var.lam != None else "\u22a5"
        print(
            f"{variable}: {analyst.ecr(type_var.uf_id)} = ref({type_tau}, {type_lambda})"
        )


def run_steensgaard_analysis(filename, variables, constraints, graph_all=False):
    """
    Runs Steensgaard's Points-to Analysis on the given variables and constraints.
    Args:
        variables (set): Set of variable names in the program.
        constraints (list): List of constraints parsed from the SIL program.
        graph_all (bool): If True, generates graphs after each constraint processing.
            Do not set to true for timing experiments.
    Returns:
        uf (UnionFind): The union-find structure representing ECRs.
        nodes (dict): Mapping from ECRs to their corresponding TypeNodes.
    """
    # Initialize the Analyst
    analyst = Analyst()

    # Initialize Type nodes for all variables
    for v in variables:
        analyst.new_type(v)

    n_constraints = len(constraints)

    if graph_all and n_constraints > 0:
        cols = int(math.ceil(math.sqrt(n_constraints + 1)))
        rows = int(math.ceil((n_constraints + 1) / cols))
        fig, axs = plt.subplots(rows, cols, figsize=(cols * 4, rows * 3))
        # Normalize axs to a flat list for easy indexing
        if isinstance(axs, plt.Axes):
            axs = [axs]
        else:
            axs = list(axs.flatten())
        # Hide any unused axes
        for i in range(n_constraints, len(axs)):
            axs[i].axis("off")

        # draw initial graph
        G = create_graph(analyst.uf, analyst.nodes)
        pos = nx.spring_layout(G)
        ax = axs[0]
        nx.draw(
            G,
            pos,
            with_labels=True,
            node_color="lightblue",
            font_weight="bold",
            font_size=8,
            node_size=300,
            arrowsize=10,
            ax=ax,
        )
        ax.set_title(f"Initial graph")
        ax.set_axis_on()

    # Process each constraint
    for i, c in enumerate(constraints):
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
            case "store":
                print("store", c["lhs"], c["rhs"])
                analyst.handle_store(c["lhs"], c["rhs"])
            case _:
                print("Unrecognized constraint.")

        print("Pending:", analyst.pending)  # debugging support
        get_debugging_types(variables, analyst)  # debugging support

        # if graph_all, draw the graph after each constraint
        if graph_all:
            G = create_graph(analyst.uf, analyst.nodes)
            pos = nx.planar_layout(G)
            ax = axs[i + 1]
            nx.draw(
                G,
                pos,
                with_labels=True,
                node_color="lightblue",
                font_weight="bold",
                font_size=8,
                node_size=300,
                arrowsize=10,
                ax=ax,
            )
            ax.set_title(f"After constraint {i + 1}")
            ax.set_axis_on()

    print("Final Types:")
    get_typing(variables, analyst)  # get the final types in the format of the paper

    if graph_all:
        output = f"{filename}_allconstraints_graphs.png"
        fig.suptitle(f"Steensgaard's Analysis Progression: {filename}")
        fig.tight_layout()
        fig.savefig(output)
        plt.close(fig)

    return analyst.uf, analyst.nodes


def save_time_analysis(
    n_constraints, n_variables, elapsed_time, filename="steensgaard_times.csv"
):
    # Add new time data points to CSV file
    df = pd.read_csv(filename)
    new_row_df = pd.DataFrame(
        [
            {
                "constraints": n_constraints,
                "variables": n_variables,
                "time": elapsed_time,
            }
        ]
    )
    # Concatenate the DataFrames
    df = pd.concat([df, new_row_df], ignore_index=True)
    df.to_csv(filename, index=False)


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

    parser.add_argument(
        "-g",
        "--graph_all",
        action="store_true",
        help="Enable intermediary graph visualizations (default: False)",
    )

    # Parse the arguments
    # If args is None, parse_args will default to sys.argv[1:]
    program_fn = parser.parse_args(args).filename
    graph_all = parser.parse_args(args).graph_all

    # Access the parsed argument (filename)
    if program_fn:
        with open(program_fn, "r") as f:
            program = f.read()
            print(program)

            ast, constraints = parse_program(program)
            n = len(constraints)  # number of constraints
            all_variables = get_all_variables(ast)
            v = len(all_variables)

            # Print important information, helpful for debugging
            print("List of all constraints:")
            print(constraints)
            print(f"\nAll variable names encountered: {sorted(all_variables)}")
            print("Parsing completed.")

            # Run Steensgaard's analysis, and time it (for performance measurement)
            start_time = time.perf_counter()
            uf, nodes = run_steensgaard_analysis(
                program_fn, all_variables, constraints, graph_all=graph_all
            )
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time

            print(
                f"\nSteensgaard's analysis on {n} constraints and {v} variables completed in {elapsed_time:.6f} seconds."
            )
            save_time_analysis(n, v, elapsed_time)
            draw_single_graph(program_fn, uf, nodes)  # graph visualization
            return 0
    else:
        print("No filename provided.")
        return -1


if __name__ == "__main__":
    # Call the main function with command-line arguments
    sys.exit(main(sys.argv[1:]))
