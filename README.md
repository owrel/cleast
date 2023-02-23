# CLingo Enriched AST (cleast)
CLingo Enriched AST (cleast) is a Python package that provides additional information and functionality for analyzing and working with an Abstract Syntax Tree (AST) generated from a logic program.

## Installation
The package can be installed using pip. The following commands should be executed:

```bash
git clone https://github.com/owrel/cleast
cd cleast
pip install .
```
## Usage
To use cleast, the Cleast class should be instantiated with the following parameters:

 - ast_list: AST of the encoding as a list
 - file: str list representing the file
 - filename: location of the file
 - src_dir: location

```python
from cleast import Cleast

ast_list = [...] # list of clingo AST
file = [...] # list of strings representing the file
filename = "file.lp"
src_dir = "directory_path"

cleast_obj = Cleast(ast_list, file, filename, src_dir)
```




