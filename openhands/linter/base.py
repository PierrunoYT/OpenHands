from pydantic import BaseModel
from abc import ABC, abstractmethod

class LintResult(BaseModel):
    file: str
    line: int  # 1-indexed
    column: int  # 1-indexed
    message: str

    def visualize(self, window_size: int = 10) -> str:
        """Visualize the lint result by print out all the lines where the lint result is found."""
        with open(self.file, 'r') as f:
            file_lines = f.readlines()

        # Add line numbers
        _span_size = len(str(len(file_lines)))
        file_lines = [
            f"{i + 1:>{_span_size}}|{line.rstrip()}"
            for i, line in enumerate(file_lines)
        ]

        # Get the window of lines to display
        assert self.line <= len(file_lines) and self.line > 0
        line_idx = self.line - 1
        begin_window = max(0, line_idx - window_size // 2)
        end_window = min(len(file_lines), line_idx + window_size // 2)
        
        selected_lines = file_lines[begin_window:end_window]
        line_idx_in_window = line_idx - begin_window

        # Add character hint
        _character_hint = (
            _span_size * " " + " " * (self.column) + "^" + " error here"
        )
        selected_lines[line_idx_in_window] = (
            f"\033[91m{selected_lines[line_idx_in_window]}\033[0m"
            + '\n'
            + _character_hint
        )
        return '\n'.join(selected_lines)
        


class LinterException(Exception):
    """Base class for all linter exceptions."""
    pass

class BaseLinter(ABC):
    """Base class for all linters.
    
    Each linter should be able to lint files of a specific type and return a list of (parsed) lint results.
    """

    encoding: str = 'utf-8'

    @property
    @abstractmethod
    def supported_extensions(self) -> list[str]:
        """The extensions that this linter supports."""
        return []

    @abstractmethod
    def lint(self, file_path: str) -> list[LintResult]:
        """Lint the given file.
        
        file_path: The path to the file to lint. Required to be absolute.
        """
        pass