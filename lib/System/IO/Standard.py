from ..Locals import PROC_DIR
from ..PyDict import load
from .File import UnOpenedFile, M_RDONLY, M_WRONLY

with open(f"{PROC_DIR}/iostreams.fakeos", 'r') as f:
	stdin_fname, stdout_fname, stderr_fname = load(f)

stdin = UnOpenedFile(stdin_fname, M_RDONLY)
stdout = UnOpenedFile(stdout_fname, M_WRONLY)
stderr = UnOpenedFile(stderr_fname, M_WRONLY)