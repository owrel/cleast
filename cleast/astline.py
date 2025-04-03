from __future__ import annotations
from enum import Enum

from clingo.ast import AST, ASTType, ASTSequence
from typing import List, Tuple, Set

from .symbol import Symbol


class ASTLineType(Enum):
    """
    Enumeration of the possible types of an ASTLine.
    """

    Rule = "Rule"
    Constraint = "Constraint"
    Fact = "Fact"
    Definition = "Definition"
    Input = "Input"
    Constant = "Constant"
    Output = "Output"


class ASTLine:
    """
    Represents a line of the logic program, encapsulating the corresponding clingo AST node and the symbols defined or used on that line.
    :param ast: The clingo AST node corresponding to the line.
    :param define: The list of symbols defined on this line.
    :param dependencies: The list of symbols used on this line.
    """

    def __init__(
        self, ast: AST, define: List[Symbol], dependencies: List[Symbol]
    ) -> None:
        self.ast = ast
        self.define = define
        self.dependencies = dependencies
        self.comments = None
        self.location = ast.location
        self.section = None
        self._identifier = None
        self.prefix = ""

    @property
    def identifier(self):
        return self._identifier

    def factory(
        ast: AST,
        define: List[Symbol],
        dependencies: List[Symbol],
        section=None,
        comments=None,
        src_dir=None,
    ):
        """
        A factory method used to create the appropriate subclass of ASTLine based on the type of the provided AST node.
        :param ast: The clingo AST node representing the logic statement.
        :param define: A list of Symbol objects representing the defined symbols in the logic statement.
        :param dependencies: A list of Symbol objects representing the dependencies in the logic statement.
        :return: An instance of the appropriate ASTLine subclass (e.g. Rule, Constraint, Fact, Definition, Input, or Output)
        """

        ret = None
        if ast.ast_type == ASTType.Rule:
            if define and dependencies:
                ret = Rule(ast, define, dependencies)
            elif define and not dependencies:
                ret = Fact(ast, define, dependencies)
            elif not define and dependencies:
                ret = Constraint(ast, define, dependencies)
            else:
                print("Problem")
        else:
            if ast.ast_type == ASTType.Defined:
                ret = Input(ast, define, dependencies)
            elif ast.ast_type == ASTType.Definition:
                ret = Definition(ast, define, dependencies)
            elif (
                ast.ast_type == ASTType.ShowSignature
                or ast.ast_type == ASTType.ShowTerm
            ):
                ret = Output(ast, define, dependencies)
            else:
                print(ast, ast.ast_type)
                print("To be ignore or not implemented yet")
        if ret:
            ret.section = section
            ret.comments = comments
            prefix = ret.location.begin.filename.replace(src_dir, "")[1:]
            prefix = prefix.replace("/", ".")
            prefix = prefix.replace(".lp", "")
            prefix += "."
            ret.prefix = prefix

        return ret

    @classmethod
    def build_ast_lines(
        cls, ast_list: List[AST], cleast: "Cleast"
    ) -> Tuple[List["ASTLine"], List["ASTLine"]]:
        """
        Builds the final AST lines, by extracting the symbols and dependencies from the given list of AST elements.
        This method will also filter the lines based on their file origin, and return the internal and external (coming from an #include statement) lines separately.

        :param ast_list: A tuple of lists containing the internal and external AST elements.
        :return: A tuple of lists containing the internal and external AST lines.
        """

        def deep_search_sym_dep(ast: AST, sym: Set, dep: Set, trace: List):
            if isinstance(ast, ASTSequence):
                trace.append("ASTSequence")
                for _ast in ast:
                    deep_search_sym_dep(_ast, sym, dep, trace)
                trace.pop()  # Remove last element
            else:
                trace.append(ast.ast_type)
                if ast.ast_type == ASTType.SymbolicAtom:
                    if "head" in trace:
                        if (
                            "head" in trace
                            and ASTType.ConditionalLiteral in trace
                            and "condition" in trace
                        ):
                            dep.add(cleast.get_symbol(ast))
                        else:
                            sym.add(cleast.get_symbol(ast))
                    elif "body":
                        dep.add(cleast.get_symbol(ast))
                    else:
                        sym.add(cleast.get_symbol(ast))
                else:
                    if ast.child_keys:
                        for child in ast.child_keys:
                            a = getattr(ast, child)
                            if a:
                                trace.append(child)
                                deep_search_sym_dep(a, sym, dep, trace)
                                trace.pop()  # Remove child from trace
                trace.pop()  # Remove ast.ast_type
                return (sym, dep)

        ast_lines = []
        external_ast_lines = []

        for ast in ast_list:
            syms, dependencies = deep_search_sym_dep(ast, set(), set(), [])
            al = ASTLine.factory(
                ast,
                syms,
                dependencies,
                section=cleast.get_section(ast),
                comments=cleast.get_comments(ast),
                src_dir=cleast.src_dir,
            )

            if al:
                if al.location.begin.filename == cleast.filename:
                    ast_lines.append(al)
                else:
                    external_ast_lines.append(al)

        return ast_lines, external_ast_lines


class Rule(ASTLine):
    def __init__(
        self, ast: AST, define: List[Symbol], dependencies: List[Symbol]
    ) -> None:
        super().__init__(ast, define, dependencies)
        self.type = ASTLineType.Rule
        self._identifier = str(list(self.define)[0].signature)


class Constraint(ASTLine):
    id = 0

    def __init__(
        self, ast: AST, define: List[Symbol], dependencies: List[Symbol]
    ) -> None:
        super().__init__(ast, define, dependencies)
        self.type = ASTLineType.Constraint
        self.id = Constraint.id
        Constraint.id += 1
        self._identifier = f"Constraint#{self.id}"


class Fact(ASTLine):
    def __init__(
        self, ast: AST, define: List[Symbol], dependencies: List[Symbol]
    ) -> None:
        super().__init__(ast, define, dependencies)
        self.type = ASTLineType.Fact
        self._identifier = str(list(self.define)[0].signature)


class Definition(ASTLine):
    def __init__(
        self, ast: AST, define: List[Symbol], dependencies: List[Symbol]
    ) -> None:
        super().__init__(ast, define, dependencies)
        self.type = ASTLineType.Definition
        self._identifier = f"{self.ast.name}"


class Input(ASTLine):
    def __init__(
        self, ast: AST, define: List[Symbol], dependencies: List[Symbol]
    ) -> None:
        super().__init__(ast, define, dependencies)
        self.type = ASTLineType.Input
        self._identifier = f"{self.ast.name}/{self.ast.arity}"


class Output(ASTLine):
    def __init__(
        self, ast: AST, define: List[Symbol], dependencies: List[Symbol]
    ) -> None:
        super().__init__(ast, define, dependencies)
        self.type = ASTLineType.Output
        if "term" in self.ast.keys():
            self._identifier = f"{self.ast.term.name}/{len(self.ast.term.arguments)}"
        else:
            self._identifier = f"{self.ast.name}/{len(self.ast.arguments)}"


class Constant(ASTLine):
    def __init__(
        self, ast: AST, define: List[Symbol], dependencies: List[Symbol]
    ) -> None:
        super().__init__(ast, define, dependencies)
        self.type = ASTLineType.Constant
        self._identifier = self.ast.name
