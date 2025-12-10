"""
Parser for a Simple Imperative Language (SIL) defined in sil_ref.txt
The parser uses the pyparsing library to define the grammar and parse the programs

The parsing actions build a useful dictionary representation of each assignment
command relevant to Steensgaard's analysis, which ignores control flow commands.

Course: COS 516
Authors: Tanvi Namjoshi & Lana Glisic

Usage:
  python sil_parser.py -fn <filename>
"""

import pyparsing as pp
import argparse
import sys


def create_sil_parser():

    # ==========================================
    # 1. Basic Tokens & Types
    # ==========================================

    # Identifiers for variable names: x, y, z, f, p etc
    identifier = pp.Word(pp.alphas, pp.alphanums + "_")

    # Integers
    number = pp.Word(pp.nums) | pp.Word(pp.nums + ".")

    operand = identifier | number

    # Punctuation
    lpar, rpar = pp.Literal("("), pp.Literal(")")
    l_brace, r_brace = pp.Literal("{"), pp.Literal("}")
    assign = pp.Literal(":=")
    semicolon = pp.Literal(";").suppress()

    # Keywords
    skip = pp.Keyword("skip")
    if_kw = pp.Keyword("if")
    then_kw = pp.Keyword("then")
    else_kw = pp.Keyword("else")
    while_kw = pp.Keyword("while")

    op_kw = pp.Keyword("add") | pp.Keyword("negate") | pp.Keyword("multiply")

    # Comments. Allows for 1-line comments starting with # (ignored when parsing)
    comment = (pp.Literal("#") + pp.SkipTo(pp.lineEnd)).suppress()

    # ==========================================
    # 2. Functions to save info for commands relevant to Steensgaard's analysis
    # ==========================================

    def cmd_assign(tokens):
        # x := y
        lhs = tokens[0]
        rhs = tokens[2]
        return {"type": "assign", "lhs": lhs, "rhs": rhs}

    def cmd_addr_of(tokens):
        # x := &y
        lhs = tokens[0]
        rhs = tokens[3]
        return {"type": "addr_of", "lhs": lhs, "rhs": rhs}

    def cmd_deref(tokens):
        # x := *y
        lhs = tokens[0]
        rhs = tokens[3]
        return {"type": "deref", "lhs": lhs, "rhs": rhs}

    def cmd_store(tokens):
        # *x := y
        lhs = tokens[1]
        rhs = tokens[3]
        return {"type": "store", "lhs": lhs, "rhs": rhs}

    def cmd_op(tokens):
        # x := op(...)
        lhs = tokens[0]
        operation = tokens[2]
        operands = tokens[4:-1]
        operand_variables = list()
        for operand in operands:
            # Only add if it's an identifier (not a number)
            if isinstance(operand, str) and operand[0].isalpha():
                operand_variables.append(operand)

        return {
            "type": "op",
            "lhs": lhs,
            "operation": operation,
            "operands": operands,
            "operand_variables": operand_variables,
        }

    def cmd_allocate(tokens):
        # x := allocate(y)
        lhs = tokens[0]
        return {"type": "allocate", "lhs": lhs}

    # We don't need any actions for any of the control flow commands
    # For if and skip, we just need to know what is inside those blocks
    # so we can parse them recursively

    # ==========================================
    # 3. Grammar Rules -- what do do with diff statements
    # ==========================================

    statement = pp.Forward()
    block = pp.Group(l_brace + pp.ZeroOrMore(statement) + r_brace)

    # Handle the different types of assignment statement s

    # x := op(...)
    op_stmt = (
        identifier + assign + op_kw + lpar + pp.delimitedList(operand) + rpar
    ).setParseAction(cmd_op)
    # x := allocate()
    allocate_stmt = (
        identifier + assign + pp.Keyword("allocate") + lpar + operand + rpar
    ).setParseAction(cmd_allocate)
    # x := &y
    addr_of_stmt = (identifier + assign + pp.Literal("&") + operand).setParseAction(
        cmd_addr_of
    )
    # x := *y
    deref_stmt = (identifier + assign + pp.Literal("*") + operand).setParseAction(
        cmd_deref
    )
    # *x := y
    store_stmt = (pp.Literal("*") + identifier + assign + operand).setParseAction(
        cmd_store
    )
    # x := y
    assign_stmt = (identifier + assign + operand).setParseAction(cmd_assign)

    assignment = (
        op_stmt | allocate_stmt | addr_of_stmt | deref_stmt | store_stmt | assign_stmt
    )

    # Handle the control flow statements (if, while , skip)
    # we only really care about the blocks inside them for now
    skip_stmt = skip.setParseAction(lambda tokens: {"type": "skip"})

    if_stmt = (
        if_kw
        + lpar
        + pp.SkipTo(rpar)
        + rpar
        + then_kw
        + block("then")
        + else_kw
        + block("else")
    ).setParseAction(
        lambda tokens: {
            "type": "if",
            "then": tokens["then"].as_list()[1:-1],
            "else": tokens["else"].as_list()[1:-1],
        },
    )

    while_stmt = (
        while_kw + lpar + pp.SkipTo(rpar) + rpar + block("body")
    ).setParseAction(
        lambda tokens: {"type": "while", "body": tokens["body"].as_list()[1:-1]},
    )

    statement <<= (if_stmt | while_stmt | skip_stmt | assignment) + semicolon | comment

    program = pp.OneOrMore(statement)
    return program


# After we have the AST, we can traverse it to get all the relevant constraints
# to do Steensgaard's analysis. This means ignoring control flow statements, and
# skip statements, but getting the constraints inside their blocks.
def get_all_constraints(ast):
    constraints = []
    for stmt in ast:
        if stmt["type"] == "if":
            constraints = (
                constraints
                + get_all_constraints(stmt["then"])
                + get_all_constraints(stmt["else"])
            )
        elif stmt["type"] == "while":
            constraints = constraints + get_all_constraints(stmt["body"])
        elif stmt["type"] == "skip":
            continue
        else:
            constraints.append(stmt)
    return constraints


def get_all_variables(ast):
    """
    Traverse the AST and return a set of all variable names encountered.

    Returns:
        set: A set containing all variable names found in the program.
    """
    variables = set()

    def extract_variables_from_stmt(stmt):
        """Helper function to extract variables from a single statement."""
        if stmt["type"] == "if":
            extract_variables_from_stmt_list(stmt["then"])
            extract_variables_from_stmt_list(stmt["else"])
        elif stmt["type"] == "while":
            extract_variables_from_stmt_list(stmt["body"])
        elif stmt["type"] == "skip":
            pass
        else:
            # Handle assignment-like statements
            if "lhs" in stmt:
                variables.add(stmt["lhs"])
            if "rhs" in stmt:
                variables.add(stmt["rhs"])
            if "operands" in stmt:
                for operand in stmt["operand_variables"]:
                    # Only add if it's an identifier (not a number)
                    variables.add(operand)

    def extract_variables_from_stmt_list(stmt_list):
        """Helper function to extract variables from a list of statements."""
        for stmt in stmt_list:
            extract_variables_from_stmt(stmt)

    extract_variables_from_stmt_list(ast)
    return variables


def main(args=None):
    # TEST with Example
    parser = argparse.ArgumentParser(
        description="A python implementation of Steensgaard's Points-to Analysis."
    )

    # Command line arguments
    parser.add_argument(
        "-fn",
        "--filename",
        type=str,
        default="tests/test.sil",
        help="Specify a filename for a SIL program.",
    )

    # Parse the arguments
    # If args is None, parse_args will default to sys.argv[1:]
    program_fn = parser.parse_args(args).filename

    print(f"Parsing SIL program from file: {program_fn}")

    # Access the parsed arguments
    with open(program_fn, "r") as f:
        program = f.read()

    parser = create_sil_parser()

    try:
        # 1. Parse the code
        ast = parser.parse_string(program)

        print("List of statement types and parsed information")

        print(f"{'STATEMENT TYPE':<15} | {'CONSTRAINT LOGIC'}")
        print("-" * 50)

        for c in ast:
            ctype = c["type"]
            logic = str(c)
            print(f"{ctype:<15} | {logic}")

        all_constraints = get_all_constraints(ast)
        print("\nList of all extracted constraints:")
        for constraint in all_constraints:
            print(constraint)

        all_variables = get_all_variables(ast)
        print(f"\nAll variable names encountered: {sorted(all_variables)}")

    except pp.ParseException as e:
        print("Parse Error:", e)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
