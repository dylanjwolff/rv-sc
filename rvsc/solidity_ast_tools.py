from io import StringIO
from solidity_parser import parser


class Unimplemented(Exception):
    pass


class CompilerVersionGetter:
    def visitPragmaDirective(self, n: parser.Node):
        self.compiler_version = n.value


def get_compiler_version(contract):
    ast = parser.parse(contract)
    cvg = CompilerVersionGetter()
    parser.visit(ast, cvg)
    return cvg.compiler_version


class SourcePrettyPrinter:
    def __init__(self, source_lines):
        self.source_lines = source_lines
        self.out_s = ""
        self.compiler_version = None

    def visitVariableDeclaration(self, n: parser.Node):
        self.visit(n.typeName)

        if get_or_default(n, "visibility", "default") != "default":
            self.out_s += f" {n.visibility} "
        if get_or_default(n, "isDeclaredConstant", False):
            self.out_s += " constant"
        if get_or_default(n, "storageLocation", False):
            self.out_s += n.storageLocation
        self.out_s += f" {n.name}"

    def visitUserDefinedTypeName(self, n: parser.Node):
        self.out_s += n.namePath

    def visitStateVariableDeclaration(self, n: parser.Node):
        for c in n.variables:
            self.visit(c)

        if get_or_default(n, "initialValue", False):
            self.out_s += " = "
            self.visit(n.initialValue)
        self.out_s += ";"

    def visitBooleanLiteral(self, n: parser.Node):
        self.out_s += str(n.value).lower()

    def visitSourceUnit(self, n):
        for c in n.children:
            self.visit(c)
        self.out_s += "\n"

    def visitMapping(self, n: parser.Node):
        self.out_s += "mapping ("
        self.visit(n.keyType)
        self.out_s += "=>"
        self.visit(n.valueType)
        self.out_s += ")"

    def visitFunctionDefinition(self, n: parser.Node):
        if n.isConstructor:
            # NOTE this is constructor in the TS pretty-printer
            self.out_s += "function "
        else:
            self.out_s += "function "

        if n.name:
            self.out_s += f"{n.name} "

        self.visit(n.parameters)

        for mod in n.modifiers:
            self.visit(mod)
            self.out_s += " "

        if n.visibility != "default":
            self.out_s += f" {n.visibility} "

        if n.stateMutability:
            self.out_s += " " + n.stateMutability

        if n.returnParameters:
            self.out_s += " returns "
            self.visit(n.returnParameters)

        if n.body:
            self.out_s += " "
            self.visit(n.body)
        else:
            self.out_s += ";"

    def visitContractDefinition(self, n: parser.Node):
        self.out_s += f"{n.kind} {n.name}"

        if len(n.baseContracts) > 0:
            self.visit_delim_list(" is ", n.baseContracts, ", ", " ")
        else:
            self.out_s += " "

        self.visit_delim_list("{\n", n.subNodes, "\n", "\n}\n\n")

    def visitInLineAssemblyStatement(self, n: parser.Node):
        self.out_s += f"{get_or_default(n, 'language', ' ')} "
        self.visit(n.body)

    def visitAssemblyBlock(self, n: parser.Node):
        self.visit_delim_list("{\n", n.operations, "\n", "}\n")

    def visitAssemblyLocalDefinition(self, n: parser.Node):
        self.out_s += "let "
        self.visit_delim_list("", n.names, ", ", "")

        self.out_s += " := "
        self.visit(n.expression)

    def visitTupleExpression(self, n: parser.Node):
        self.visit_delim_list("(", n.components, ", ", ")")

    def visitReturnStatement(self, n: parser.Node):
        self.out_s += "return "
        if (n.expression):
            self.visit(n.expression)
        self.out_s += ";"

    def visitAssemblyAssignment(self, n: parser.Node):
        self.visit_delim_list("{", n.names, ", ", "} := ")
        self.visit(n.expression)

    def visitAssemblyCall(self, n: parser.Node):
        self.out_s += n.functionName
        self.visit_delim_list("(", n.arguments, ", ", ")")

    def visitAssemblyExpression(self, n: parser.Node):
        self.out_s += n.functionName
        self.visit_delim_list("(", n.arguments, ", ", ")")

    def visitHexLiteral(self, n: parser.Node):
        self.out_s += n.value

    def visitHexNumber(self, n: parser.Node):
        self.out_s += n.value

    def visitDecimalNumber(self, n: parser.Node):
        self.out_s += n.value

    def visitStringLiteral(self, n: parser.Node):
        self.out_s += f'"{n.value}"'

    def visitNumberLiteral(self, n: parser.Node):
        self.out_s += n.number

    def visitBinaryOperation(self, n: parser.Node):
        self.visit(n.left)
        self.out_s += f" {n.operator} "
        self.visit(n.right)

    def visitIfStatement(self, n: parser.Node):
        self.out_s += "if ("
        self.visit(n.condition)
        self.out_s += ") "
        self.visit(n.TrueBody)
        if n.FalseBody:
            self.out_s += " else "
            self.visit(n.FalseBody)

    def visitForStatement(self, n: parser.Node):
        self.out_s += "for ("

        if n.initExpression:
            self.visit(n.initExpression)
        else:
            self.out_s += ";"

        self.out_s += " "
        self.visit(n.conditionExpression)
        self.out_s += "; "
        if (n.loopExpression):
            self.visit(n.loopExpression.expression)

        self.out_s += ") "
        self.visit(n.body)

    def visitFunctionCall(self, n: parser.Node):
        self.visit(n.expression)
        self.out_s += "("
        if len(n.names) > 0:
            self.out_s += "{ "
            self.out_s += f"{n.names[0]} : "
            self.visit(n.arguments[0])
            for (name, arg) in zip(n.names[1:], n.arguments[1:]):
                self.out_s += ", "
                self.out_s += f"{name} : "
                self.visit(arg)
            self.out_s += " }"
        elif len(n.arguments) > 0:
            self.visit(n.arguments[0])
            for arg in n.arguments[1:]:
                self.out_s += ", "
                self.visit(arg)
        self.out_s += ")"

    def visitElementaryTypeName(self, n: parser.Node):
        self.out_s += n.name

    def visitIdentifier(self, n: parser.Node):
        self.out_s += n.name

    def visitBlock(self, n: parser.Node):
        self.out_s += "{\n"
        for stmt in n.statements:
            if stmt == None:
                continue
            self.out_s += "\t"
            if "return" in self.source_lines[stmt.loc["start"]["line"] - 1]:
                self.out_s += "return "
                self.visit(stmt)
                self.out_s += ";\n"
            else:
                self.visit(stmt)
            self.out_s += "\n"

        self.out_s += "}\n"

    def visitVariableDeclarationStatement(self, n: parser.Node):
        if len(n.variables) > 1:
            self.visit_delim_list("(", n.variables, ", ", ")")
        elif len(n.variables) == 1:
            self.visit(n.variables[0])
        if n.initialValue:
            self.out_s += " = "
            self.visit(n.initialValue)
        self.out_s += ";"

    def visitUnaryOperation(self, n: parser.Node):
        if n.isPrefix:
            self.out_s += n.operator + " "

        self.visit(n.subExpression)
        if not n.isPrefix:
            self.out_s += " " + n.operator

    def visitArrayTypeName(self, n: parser.Node):
        self.visit(n.baseTypeName)
        self.out_s += "["
        if n.length:
            self.visit(n.length)
        self.out_s += "]"

    def visitMemberAccess(self, n: parser.Node):
        self.visit(n.expression)
        self.out_s += "." + n.memberName

    def visitExpressionStatement(self, n: parser.Node):
        self.visit(n.expression)
        self.out_s += ";"

    def visitIndexAccess(self, n: parser.Node):
        self.visit(n.base)
        self.out_s += "["
        self.visit(n.index)
        self.out_s += "]"

    def visitPragmaDirective(self, n: parser.Node):
        self.compiler_version = n.value
        self.out_s += f"pragma {n.name} {n.value};\n"

    def visitParameterList(self, n):
        self.visit_delim_list("(", n.parameters, ", ", ")")

    def visitParameter(self, n):
        self.visit(n.typeName)
        if n.name:
            self.out_s += f" {n.name}"

    def visitInheritanceSpecifier(self, n: parser.Node):
        self.visit(n.baseName)

    def visitElementaryTypeNameExpression(self, n: parser.Node):
        self.visit(n.typeName)

    def visitModifierInvocation(self, n: parser.Node):
        self.out_s += f" {n.name}"
        if len(n.arguments) > 0:
            self.visit_delim_list("(", n.arguments, ", ", ")")

    def visitEventDefinition(self, n: parser.Node):
        self.out_s += f"event {n.name}"
        self.visit(n.parameters)
        self.out_s += ";"

    def visitModifierDefinition(self, n: parser.Node):
        self.out_s += f"modifier {n.name}"
        self.visit(n.parameters)
        self.visit(n.body)

    def visitNewExpression(self, n: parser.Node):
        self.out_s += "new "
        self.visit(n.typeName)

    def visitUsingForDeclaration(self, n: parser.Node):
        self.out_s += f"using {n.libraryName} for "
        self.visit(n.typeName)
        self.out_s += ";"

    def visitEnumDefinition(self, n: parser.Node):
        self.out_s += f"enum {n.name} "
        self.visit_delim_list("{", n.members, ", ", "}")

    def visitEnumValue(self, n: parser.Node):
        self.out_s += f"{n.name} "

    def visitEmitStatement(self, n: parser.Node):
        self.out_s += f"emit "
        self.visit(n.eventCall)
        self.out_s += f";"

    def visitStructDefinition(self, n: parser.Node):
        self.out_s += f"struct {n.name}"
        self.visit_delim_list("{", n.members, ";\n", "}", always_sep=True)

    def visit_delim_list(self,
                         before: str,
                         items,
                         sep: str,
                         after: str,
                         always_sep=False):
        self.out_s += before
        if len(items) > 0:
            self.visit(items[0])
            if always_sep:
                self.out_s += sep
            for item in items[1:]:
                self.out_s += sep
                self.visit(item)
        self.out_s += after

    def visit(self, n):
        if type(n) == list:
            for c in n:
                self.visit(c)
            return
        method_name = "visit" + n.type
        if hasattr(self, method_name):
            return getattr(self, method_name)(n)
        else:
            if empty_loc(n.loc) or has_child(n):
                raise Unimplemented(n)
            print(n)
            self.out_s += f"{substr_from_loc(self.source_lines, n.loc)}"


def has_child(n: parser.Node):
    for attr in n.keys():
        if type(n[attr]) == parser.Node:
            return True
        if type(n[attr]) == list:
            if len(n[attr]) > 0:
                if type(n[attr][0]) == parser.Node:
                    return True
    return False


def empty_loc(a):
    return a["start"]["line"] == a["end"]["line"] \
        and a["start"]["column"] == a["end"]["column"]


def get_or_default(n, attr, default):
    try:
        return getattr(n, attr)
    except KeyError:
        return default


def substr_from_loc(lines, loc):
    start_line = loc["start"]["line"] - 1
    start_col = loc["start"]["column"]
    end_line = loc["end"]["line"] - 1
    end_col = loc["end"]["column"]
    if start_line == end_line:
        return lines[start_line][start_col:end_col]
    else:
        s = lines[start_line][start_col:]
        for lnum in range(start_line + 1, end_line - 1):
            s += lines[lnum]
        s += lines[end_line][0:end_col]
        return s