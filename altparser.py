import sys

#####################################
# TOKENIZER
#####################################

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value:
            return f"{self.type}({self.value})"
        return f"{self.type}"


def tokenize(src):
    i = 0
    tokens = []
    while i < len(src):
        c = src[i]

        # Skip whitespace
        if c.isspace():
            i += 1
            continue

        # Single character tokens
        if c in ";(),*=&<>={}":
            tokens.append(Token(c))
            i += 1
            continue

        # Multi-character operators
        if src.startswith("==", i):
            tokens.append(Token("EQ"))
            i += 2
            continue

        if src.startswith("->", i):
            tokens.append(Token("ARROW"))
            i += 2
            continue

        # Keywords
        for kw in ["if", "then", "else", "while", "do", "skip",
                   "add", "mul", "neg", "alloc", "fun"]:
            # Check keyword and identifier are not confused
            if src.startswith(kw, i) and (i+len(kw) == len(src) or not (src[i+len(kw)].isalnum() or src[i+len(kw)] == '_')):
                tokens.append(Token("KW", kw))
                i += len(kw)
                break
        else:
            # Variable identifier
            if c.isalpha():
                start = i
                while i < len(src) and (src[i].isalnum() or src[i] == "_"):
                    i += 1
                ident = src[start:i]
                tokens.append(Token("ID", ident))
                continue

            # Number
            if c.isdigit():
                start = i
                while i < len(src) and src[i].isdigit():
                    i += 1
                num = src[start:i]
                tokens.append(Token("NUM", num))
                continue

            raise Exception(f"Unexpected character: {c}")

    tokens.append(Token("EOF"))
    return tokens


#####################################
# PARSER (recursive)
#####################################

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0

    def peek(self):
        return self.tokens[self.i]

    def eat(self, type_, value=None):
        tok = self.peek()
        if tok.type != type_ and tok.value != value:
            raise Exception(f"Expected {type_}, got {tok}")
        self.i += 1
        return tok

    ###################################
    # Expressions
    ###################################
    def parse_expr(self):
        tok = self.peek()

        if tok.type == "NUM":
            return ("num", self.eat("NUM").value)

        if tok.type == "ID":
            return ("var", self.eat("ID").value)

        if tok.type == "*":
            self.eat("*")
            v = self.eat("ID").value
            return ("deref", v)

        if tok.type == "&":
            self.eat("&")
            v = self.eat("ID").value
            return ("addr", v)

        raise Exception(f"Invalid expression start: {tok}")

    ###################################
    # Conditions
    ###################################
    def parse_condition(self):
        left = self.parse_expr()
        op = self.peek()

        if op.type in ("<", "<=", "=", "EQ"):
            self.eat(op.type)
        else:
            raise Exception(f"Expected comparison operator, got {op}")

        right = self.parse_expr()
        return ("cmp", op.type, left, right)

    ###################################
    # Statement helpers
    ###################################
    def is_statement_start(self, tok):
        if tok.type == "KW" and tok.value in ("if", "while", "skip"):
            return True
        if tok.type == "ID":
            return True
        if tok.type == "{":
            return True
        return False

    ###################################
    # Simple statements
    ###################################
    def parse_simple_statement(self):
        tok = self.peek()

        # skip;
        if tok.type == "KW" and tok.value == "skip":
            self.eat("KW", "skip")
            self.eat(";")
            return ("skip",)

        # if condition then S else S;
        if tok.type == "KW" and tok.value == "if":
            self.eat("KW", "if")
            cond = self.parse_condition()
            self.eat("KW", "then")
            s1 = self.parse_statement()
            self.eat("KW", "else")
            s2 = self.parse_statement()
            self.eat(";")
            return ("if", cond, s1, s2)

        # while condition do S;
        if tok.type == "KW" and tok.value == "while":
            self.eat("KW", "while")
            cond = self.parse_condition()
            self.eat("KW", "do")
            body = self.parse_statement()
            self.eat(";")
            return ("while", cond, body)

        # { S }   (NO semicolon after block)
        if tok.type == "{":
            self.eat("{")
            s = self.parse_statement()
            self.eat("}")
            return s

        # ID = something;
        if tok.type == "ID":
            lhs = self.eat("ID").value
            self.eat("=")

            # fun
            if self.peek().type == "KW" and self.peek().value == "fun":
                self.eat("KW", "fun")
                self.eat("(")
                args = self.parse_idlist()
                self.eat(")")
                self.eat("ARROW")
                self.eat("(")
                rets = self.parse_idlist()
                self.eat(")")
                self.eat("{")
                body = self.parse_statement()
                self.eat("}")
                self.eat(";")
                return ("fun", lhs, args, rets, body)

            # call
            if self.peek().type == "ID":
                fname = self.eat("ID").value
                if self.peek().type == "(":
                    self.eat("(")
                    args = self.parse_arglist()
                    self.eat(")")
                    self.eat(";")
                    return ("call", lhs, fname, args)

            # assignment
            expr = self.parse_expr()
            self.eat(";")
            return ("assign", lhs, expr)

        raise Exception(f"Unexpected start of statement: {tok}")

    ###################################
    # Full statement with sequencing
    ###################################
    def parse_statement(self):
        stmt = self.parse_simple_statement()

        # Sequence: keep parsing while another statement begins
        while self.is_statement_start(self.peek()):
            right = self.parse_simple_statement()
            stmt = ("seq", stmt, right)

        return stmt

    ###################################
    # Lists
    ###################################
    def parse_arglist(self):
        args = []
        if self.peek().type in ("ID", "NUM", "*", "&"):
            args.append(self.parse_expr())
            while self.peek().type == ",":
                self.eat(",")
                args.append(self.parse_expr())
        return args

    def parse_idlist(self):
        ids = []
        if self.peek().type == "ID":
            ids.append(self.eat("ID").value)
            while self.peek().type == ",":
                self.eat(",")
                ids.append(self.eat("ID").value)
        return ids


#####################################
# MAIN
#####################################

def main():
    program = sys.stdin.read()
    tokens = tokenize(program)
    parser = Parser(tokens)
    ast = parser.parse_statement()
    print("AST:")
    print(ast)

if __name__ == "__main__":
    main()
