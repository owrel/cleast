from __future__ import annotations
from clingo.ast import Location, Position
from typing import List

from .utils import parse_content_from_location


class Comment:
    def __init__(self, location: Location, large_comment: bool, content: str) -> None:
        self.location = location
        self.large_comment = large_comment
        self.content = content

    @classmethod
    def extract_comments(cls, file: List[str], filename=str) -> List[Comment]:
        import re

        comments = []

        # Find single-line comments (% followed by anything except *)
        single_line_pattern = re.compile(r"%(?!\*)(.*?)$")

        # Find multi-line comments start and end
        multi_line_start = re.compile(r"%\*(.*?)$")
        multi_line_end = re.compile(r"^(.*?)\*%")

        in_comment = False
        begin = None
        comment_content = ""

        for idx_row, line in enumerate(file):
            if not in_comment:
                # Check for single-line comment
                match = single_line_pattern.search(line)
                if match:
                    begin_col = match.start()
                    begin = Position(filename, idx_row, begin_col + 1)
                    location = Location(begin, Position(filename, idx_row, len(line)))
                    content = line[begin_col + 1 :].strip()
                    comments.append(Comment(location, False, content))

                # Check for multi-line comment start
                match = multi_line_start.search(line)
                if match:
                    begin_col = match.start()
                    begin = Position(filename, idx_row, begin_col + 1)
                    comment_content = line[begin_col + 2 :] + "\n"
                    in_comment = True
            else:
                # Check for multi-line comment end
                match = multi_line_end.search(line)
                if match:
                    end_col = match.end()
                    comment_content += line[: end_col - 2]
                    location = Location(begin, Position(filename, idx_row, end_col - 1))
                    comments.append(Comment(location, True, comment_content))
                    in_comment = False
                else:
                    comment_content += line

        return comments

    def __repr__(self) -> str:
        return self.content
