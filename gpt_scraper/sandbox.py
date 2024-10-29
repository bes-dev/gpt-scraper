import ast
import builtins
import logging
from typing import Any, Dict, List, Optional, Set, Callable
from types import FunctionType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sandbox")


# Define a set of safe modules that are allowed to be imported
SAFE_MODULES: Set[str] = {
    'math',
    'json',
    're',
    'datetime',
    'logging',
    'typing',
    'bs4',  # BeautifulSoup
    # Add other modules that you deem safe
}


def extract_imports(code: str) -> Set[str]:
    """
    Parses the code and extracts all imported module names.

    Args:
        code (str): The Python code to analyze.

    Returns:
        Set[str]: A set of module names that are imported in the code.
    """
    tree = ast.parse(code)
    imports = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])

    logger.debug(f"Extracted imports: {imports}")
    return imports


def safe_import(
    name: str,
    globals: Optional[Dict[str, Any]] = None,
    locals: Optional[Dict[str, Any]] = None,
    fromlist: Optional[List[str]] = None,
    level: int = 0
) -> Any:
    """
    A custom __import__ function that restricts imports to SAFE_MODULES only.

    Args:
        name (str): The name of the module to import.
        globals (dict, optional): Not used.
        locals (dict, optional): Not used.
        fromlist (list, optional): Not used.
        level (int, optional): Not used.

    Returns:
        module: The imported module if allowed.

    Raises:
        ImportError: If the module is not in the SAFE_MODULES list.
    """
    if name in SAFE_MODULES:
        logger.debug(f"Importing allowed module: {name}")
        return builtins.__import__(name, globals, locals, fromlist, level)
    else:
        logger.error(f"Attempted to import disallowed module: {name}")
        raise ImportError(f"Importing module '{name}' is not allowed.")


def execute_sandboxed(
    code: str,
    html_content: str
) -> List[Dict[str, Optional[str]]]:
    """
    Executes the provided code in a restricted environment and calls the parse function.

    Args:
        code (str): The code containing the parse function.
        html_content (str): The HTML content to parse.

    Returns:
        List[Dict[str, Optional[str]]]: The result from the parse function.

    Raises:
        ImportError: If the code contains disallowed imports.
        ValueError: If the 'parse' function is not defined properly.
        Exception: If any other error occurs during execution.
    """
    # Step 1: Extract and validate imports
    imported_modules = extract_imports(code)
    disallowed_modules = imported_modules - SAFE_MODULES
    if disallowed_modules:
        logger.error(f"Disallowed modules detected: {disallowed_modules}")
        raise ImportError(f"The following modules are not allowed: {disallowed_modules}")

    # Step 2: Prepare restricted built-ins, including the custom __import__
    restricted_builtins: Dict[str, Any] = {
        'abs': abs,
        'bool': bool,
        'dict': dict,
        'float': float,
        'int': int,
        'len': len,
        'list': list,
        'max': max,
        'min': min,
        'range': range,
        'str': str,
        'print': print,          # Optionally allow print
        '__import__': safe_import,  # Include the custom __import__ here
        'Exception': Exception,          # Add Exception class
        'AttributeError': AttributeError,  # Add AttributeError class
        # Add other safe built-ins as needed
    }

    # Step 3: Define the global execution environment
    restricted_globals: Dict[str, Any] = {
        '__builtins__': restricted_builtins,
        'logging': logging,  # Allow logging if needed by the code
    }

    try:
        # Step 4: Execute the code with restricted_globals as both globals and locals
        exec(code, restricted_globals)
        logger.info("Code executed successfully in sandbox.")

        # Step 5: Retrieve the parse function from restricted_globals
        parse_func: Optional[FunctionType] = restricted_globals.get('parse')
        if not isinstance(parse_func, FunctionType):
            logger.error("The 'parse' function is not defined properly in the provided code.")
            raise ValueError("The 'parse' function is not defined properly in the provided code.")

        # Step 6: Call the parse function with the provided HTML content
        result = parse_func(html_content)
        logger.info("Parse function executed successfully.")
        return result

    except Exception as e:
        logger.exception(f"An error occurred during sandboxed execution: {e}")
        raise
