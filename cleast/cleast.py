from __future__ import annotations
from typing import List, Dict
from clingo.ast import AST, ASTType
# Local import
from .directive import Directive
from .symbol import Symbol
from .variable import Variable
from .astline import ASTLine, ASTLineType
from .comment import Comment



class Cleast:
    """
    CLingo Enriched AST (cleast) class provides additional information and functionality for analyzing and working with an Abstract Syntax Tree (AST) generated from a logic program. 
    This class takes as input a list of AST objects, the lines of the source file as a list of strings, the filename to the source file and the directory.

    :param ast_list: AST of the encoding as a list
    :param file: str list representing the file
    :param filename: location of the file
    :param src_dir: location
    """

    def __init__(self,
                 ast_list: List[AST],
                 file: List[str],
                 filename: str,
                 src_dir: str,
                 ) -> None:

        self.file = file
        self.filename = filename
        self.src_dir = src_dir

        self.directives = Directive.extract_directives(
            self.file, self.filename)

        self.comments = Comment.extract_comments(file, filename)

        self.symbols = Symbol.extract_symbols(
            ast_list, self.directives.get('predicates'), filename)

        self.variables = Variable.extract_variables(
            ast_list, self.directives.get('var'), filename)

        self.ast_lines, self.external_ast_lines = ASTLine.build_ast_lines(
            ast_list, self)
        
    # Private methods    
    def get_comments(self, ast: AST) -> List[Comment]:
        """
        Return a list of comments associated to the 

        :param ast: The AST node for which to fetch comments.
        :param file: A list of strings representing the lines of the logic program file.
        :return: A list of comments.
        """
        ret = []
        line_number = ast.location.begin.line
        for comment in self.comments:
            if line_number == comment.location.begin.line:
                ret.append(comment)

        return ret

    def get_sections(self, obj) -> Directive | None:
        """
        Given an object with a location attribute, returns the section directive that the object belongs to. 
        If no associated section directive is found, returns None.

        :param obj: An object with a location attribute, such as an AST node or a Symbol.
        :return: The section Directive that the object belongs to, or None if no associated section directive is found.
        """
        line = obj.location.begin.line - 1
        current_section = None
        if self.directives.get('section'):
            for section in sorted(self.directives['section'], key=lambda directive: directive.line_number):
                if section.line_number < line:
                    current_section = section
                else:
                    break
        return current_section

    def get_symbol(self, ast: ASTType.SymbolicAtom):
        """
        Given an AST symbolic atom, returns the Symbol object already computed that corresponds to it.

        :param ast: The AST symbolic atom to find the corresponding Symbol for.
        :return: The Symbol object corresponding to the given AST symbolic atom, or None if no such symbol is found.
        """
        for symbol in self.symbols:
            if ast.symbol.name == symbol.name and ast.symbol.location == symbol.location:
                return symbol

        return Symbol(ast, None)

    # Pulic methods
    def get_line(self, line: int):
        """
        Given a line number, returns every element at this line position

        :param line: line number where the elements needs to be retrieve
        :return: A list of element
        """
        ret = []
        all_elem = []
        all_elem.extend(self.directives)
        all_elem.extend(self.comments)
        all_elem.extend(self.variables)
        all_elem.extend(self.ast_lines)

        for elem in all_elem:
            if elem.location.begin.line == line or elem.location.begin.line-1 == line:
                ret.append(ret)
        return ret


    def get_ast_lines(self,
                      kind: ASTLineType | None = None,
                      local: bool = False):
        all_ast = self.ast_lines.copy()
        if not local : all_ast.extend(self.external_ast_lines)
        
        if kind:
            return [ast_line for ast_line in all_ast if ast_line.type == kind]
        else:
            return all_ast
