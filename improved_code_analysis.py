import ast
import re
import inspect
from typing import List, Dict, Any, Optional, Union


def analyze_python_code(code_blocks: List[str]) -> List[Dict[str, Any]]:
    """
    Advanced analysis of Python code blocks using the ast module to extract
    functions, classes, method calls, and dependencies.

    Args:
        code_blocks: List of Python code strings to analyze

    Returns:
        List of dictionaries containing analysis of each module
    """
    block_modules = []

    for i, code in enumerate(code_blocks):
        try:
            # Parse the code block using ast
            tree = ast.parse(code)

            # Initialize the module info
            module_info = {
                "id": f"block_{i}",
                "functions": [],
                "classes": [],
                "function_calls": [],
                "imports": [],
                "relationships": [],
            }

            # Extract functions, classes, and function calls
            for node in ast.walk(tree):
                # Extract function definitions
                if isinstance(node, ast.FunctionDef):
                    # Get function arguments safely
                    args = []
                    if hasattr(node.args, "args"):
                        args = [
                            arg.arg
                            for arg in node.args.args
                            if hasattr(arg, "arg") and arg.arg != "self"
                        ]

                    module_info["functions"].append(
                        {"name": node.name, "args": args, "line": node.lineno}
                    )

                # Extract class definitions
                elif isinstance(node, ast.ClassDef):
                    methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            methods.append(item.name)

                    bases = []
                    for base in node.bases:
                        if isinstance(base, ast.Name) and hasattr(base, "id"):
                            bases.append(base.id)

                    module_info["classes"].append(
                        {
                            "name": node.name,
                            "methods": methods,
                            "bases": bases,
                            "line": node.lineno,
                        }
                    )

                # Extract function calls
                elif isinstance(node, ast.Call):
                    func_name = None
                    if isinstance(node.func, ast.Name):
                        func_name = node.func.id
                    elif isinstance(node.func, ast.Attribute) and hasattr(
                        node.func, "attr"
                    ):
                        func_name = node.func.attr

                    if func_name:
                        module_info["function_calls"].append(
                            {"name": func_name, "line": getattr(node, "lineno", 0)}
                        )

                # Extract import statements
                elif isinstance(node, ast.Import):
                    for name in node.names:
                        if hasattr(name, "name"):
                            module_info["imports"].append(name.name)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_info["imports"].append(f"{node.module}")

            # Determine module name or main function/class
            if module_info["functions"] or module_info["classes"]:
                main_elements = []
                if module_info["functions"]:
                    main_elements.append(f"{module_info['functions'][0]['name']}()")
                if module_info["classes"]:
                    main_elements.append(f"class {module_info['classes'][0]['name']}")

                module_info["main_name"] = " & ".join(main_elements)
            else:
                # Try to extract filename or comment to name the module
                filename_match = re.search(r"#\s*(.+\.py)", code)
                if filename_match:
                    module_info["main_name"] = filename_match.group(1)
                else:
                    module_info["main_name"] = f"Module {i + 1}"

            block_modules.append(module_info)

        except SyntaxError:
            # Handle syntax errors gracefully
            block_modules.append(
                {
                    "id": f"block_{i}",
                    "main_name": f"Code Block {i + 1} (Syntax Error)",
                    "functions": [],
                    "classes": [],
                    "function_calls": [],
                    "imports": [],
                    "relationships": [],
                }
            )

    # Analyze cross-module relationships
    analyze_relationships(block_modules)

    return block_modules


def analyze_relationships(modules: List[Dict[str, Any]]) -> None:
    """
    Analyze relationships between modules based on imports and function calls.

    Args:
        modules: List of module info dictionaries to analyze
    """
    # Create a map of function and class names to their modules
    name_to_module = {}

    for module in modules:
        for func in module["functions"]:
            name_to_module[func["name"]] = module["id"]

        for cls in module["classes"]:
            name_to_module[cls["name"]] = module["id"]

    # Find relationships based on function calls and imports
    for module in modules:
        # Check function calls
        for call in module["function_calls"]:
            if (
                call["name"] in name_to_module
                and name_to_module[call["name"]] != module["id"]
            ):
                module["relationships"].append(
                    {
                        "from": module["id"],
                        "to": name_to_module[call["name"]],
                        "type": "calls",
                        "label": f"calls {call['name']}()",
                    }
                )

        # Check imports (simplified)
        for imp in module["imports"]:
            parts = imp.split(".")
            if parts[0] in name_to_module and name_to_module[parts[0]] != module["id"]:
                module["relationships"].append(
                    {
                        "from": module["id"],
                        "to": name_to_module[parts[0]],
                        "type": "imports",
                        "label": f"imports",
                    }
                )


def identify_function_calls(code: str) -> List[str]:
    """
    Use regex to identify function calls in a code snippet.
    This is used as a fallback when AST parsing fails.

    Args:
        code: Python code as a string

    Returns:
        List of function call names
    """
    # Pattern to match function calls: name(args)
    pattern = r"([a-zA-Z_][a-zA-Z0-9_]*)\s*\("
    calls = re.findall(pattern, code)
    # Filter out common Python keywords that might be matched
    keywords = [
        "if",
        "for",
        "while",
        "with",
        "print",
        "len",
        "range",
        "int",
        "str",
        "list",
        "dict",
    ]
    return [call for call in calls if call not in keywords]


def sanitize_for_mermaid(text: str) -> str:
    """
    Sanitize text to be safely displayed in Mermaid nodes.
    Escapes quotes and other special characters.

    Args:
        text: Text to sanitize

    Returns:
        Sanitized text safe for Mermaid diagrams
    """
    if not text:
        return ""

    # Replace quotes and other special characters
    escaped = text.replace('"', '\\"').replace("\\", "\\\\")

    # Truncate overly long strings
    if len(escaped) > 30:
        escaped = escaped[:27] + "..."

    return escaped


def sanitize_id(text: str) -> str:
    """
    Sanitize text to be used as a node ID in Mermaid.
    Removes special characters and spaces.

    Args:
        text: Text to sanitize into an ID

    Returns:
        Sanitized ID safe for Mermaid
    """
    if not text:
        return "unknown"

    # Replace special characters with underscores
    return re.sub(r"[^\w]", "_", text)


def generate_improved_mermaid(code_blocks: List[str]) -> str:
    """
    Generate a robust Mermaid flowchart from Python code blocks
    with proper escaping and syntax validation.

    Args:
        code_blocks: List of Python code strings

    Returns:
        Mermaid diagram code as a string
    """
    # Analyze the code blocks
    modules = analyze_python_code(code_blocks)

    # Start generating the Mermaid code
    mermaid_code = "flowchart TD\n"

    # Add style definitions
    mermaid_code += "    %% Node styles\n"
    mermaid_code += "    classDef module fill:#f5f5f5,stroke:#333,stroke-width:1px\n"
    mermaid_code += (
        "    classDef function fill:#e1f5e1,stroke:#4CAF50,stroke-width:1px\n"
    )
    mermaid_code += (
        "    classDef classObj fill:#e3f2fd,stroke:#2196F3,stroke-width:1px\n"
    )
    mermaid_code += (
        "    classDef mainModule fill:#fff8e1,stroke:#FFC107,stroke-width:2px\n\n"
    )

    # Process each module
    for module in modules:
        # Sanitize module name
        module_id = module["id"]
        module_name = sanitize_for_mermaid(module["main_name"])

        # Determine if this is likely a main module
        is_main = False
        for func in module["functions"]:
            if func["name"] == "main":
                is_main = True
                break

        # Check filename patterns for main modules
        if (
            is_main
            or "app.py" in module_name.lower()
            or "main.py" in module_name.lower()
        ):
            mermaid_code += f'    {module_id}["{module_name}"]:::mainModule\n'
        else:
            mermaid_code += f'    {module_id}["{module_name}"]:::module\n'

        # Add subgraphs for module content if it has functions or classes
        if module["functions"] or module["classes"]:
            mermaid_code += f'    subgraph {module_id}_content["{sanitize_for_mermaid(module["main_name"])} Content"]\n'

            # Add function nodes
            for func in module["functions"]:
                func_name = sanitize_for_mermaid(func["name"])
                func_id = f"{module_id}_f_{sanitize_id(func['name'])}"
                args_text = ", ".join(func["args"])

                # Truncate args text if too long
                if len(args_text) > 20:
                    args_text = args_text[:17] + "..."

                mermaid_code += (
                    f'        {func_id}("{func_name}({args_text})"):::function\n'
                )

            # Add class nodes
            for cls in module["classes"]:
                cls_name = sanitize_for_mermaid(cls["name"])
                cls_id = f"{module_id}_c_{sanitize_id(cls['name'])}"

                # Add class bases if any
                if cls["bases"]:
                    base_text = f" : {', '.join(cls['bases'])}"
                    if len(base_text) > 20:
                        base_text = base_text[:17] + "..."
                    mermaid_code += (
                        f'        {cls_id}["class {cls_name}{base_text}"]:::classObj\n'
                    )
                else:
                    mermaid_code += f'        {cls_id}["class {cls_name}"]:::classObj\n'

                # Add method nodes if there are methods
                for method in cls["methods"]:
                    method_id = f"{cls_id}_m_{sanitize_id(method)}"
                    method_name = sanitize_for_mermaid(method)
                    mermaid_code += (
                        f'        {method_id}["{method_name}()"]:::function\n'
                    )
                    mermaid_code += f"        {cls_id} --> {method_id}\n"

            mermaid_code += "    end\n\n"

            # Connect module to its functions and classes
            for func in module["functions"]:
                func_id = f"{module_id}_f_{sanitize_id(func['name'])}"
                mermaid_code += f"    {module_id} --> {func_id}\n"

            for cls in module["classes"]:
                cls_id = f"{module_id}_c_{sanitize_id(cls['name'])}"
                mermaid_code += f"    {module_id} --> {cls_id}\n"

    # Add relationships between modules
    mermaid_code += "\n    %% Module relationships\n"
    added_relationships = []

    for module in modules:
        for rel in module["relationships"]:
            # Create a unique relationship identifier
            rel_key = f"{rel['from']}|{rel['to']}|{rel['type']}"

            # Only add the relationship if it hasn't been added before
            if rel_key not in added_relationships:
                # Fix: Properly escape and simplify the relationship label
                label = sanitize_for_mermaid(rel["label"])
                # Avoid problematic characters in relationship labels
                label = label.replace("(", "").replace(")", "").replace("|", "-")

                # Keep labels very simple to avoid parsing errors
                if "calls" in label:
                    label = "calls"
                elif "imports" in label:
                    label = "imports"

                mermaid_code += f"    {rel['from']} -->|{label}| {rel['to']}\n"
                added_relationships.append(rel_key)

    # If no explicit relationships found, add sequential flow
    if not added_relationships and len(modules) > 1:
        mermaid_code += "\n    %% Sequential flow (fallback)\n"
        for i in range(len(modules) - 1):
            current_id = modules[i]["id"]
            next_id = modules[i + 1]["id"]
            # Fix: Simplify the label to avoid parsing errors
            mermaid_code += f"    {current_id} -.->|flow| {next_id}\n"

    return mermaid_code


def generate_detailed_mermaid(code_blocks: List[str]) -> str:
    """
    Generate a detailed Mermaid flowchart based on advanced code analysis.
    This is a more resilient version of the original function.

    Args:
        code_blocks: List of Python code strings to analyze

    Returns:
        Mermaid diagram code as a string
    """
    return generate_improved_mermaid(code_blocks)


def extract_module_summary(code_blocks: List[str]) -> Dict[str, Any]:
    """
    Extract a high-level summary of the code with function and class counts

    Args:
        code_blocks: List of Python code strings

    Returns:
        Dictionary with summary information
    """
    modules = analyze_python_code(code_blocks)

    # Count total functions, classes, lines, etc.
    total_functions = sum(len(module["functions"]) for module in modules)
    total_classes = sum(len(module["classes"]) for module in modules)
    total_imports = sum(len(module["imports"]) for module in modules)

    # Count unique imports
    all_imports = set()
    for module in modules:
        for imp in module["imports"]:
            all_imports.add(imp)

    # Find the "main" module
    main_module = None
    for module in modules:
        for func in module["functions"]:
            if func["name"] == "main":
                main_module = module["main_name"]
                break
        if main_module:
            break

    return {
        "module_count": len(modules),
        "function_count": total_functions,
        "class_count": total_classes,
        "import_count": len(all_imports),
        "unique_imports": sorted(list(all_imports)),
        "main_module": main_module,
        "modules": [m["main_name"] for m in modules],
    }


def generate_architecture_report(code_blocks: List[str]) -> str:
    """
    Generate a markdown report describing the architecture of the code

    Args:
        code_blocks: List of Python code strings

    Returns:
        Markdown formatted architecture report
    """
    modules = analyze_python_code(code_blocks)
    summary = extract_module_summary(code_blocks)

    report = f"# Architecture Report\n\n"
    report += f"## Overview\n\n"
    report += f"This project consists of {summary['module_count']} modules with "
    report += f"{summary['function_count']} functions and {summary['class_count']} classes.\n\n"

    if summary["main_module"]:
        report += (
            f"The main entry point appears to be in: **{summary['main_module']}**\n\n"
        )

    report += f"## Module Breakdown\n\n"

    for module in modules:
        report += f"### {module['main_name']}\n\n"

        # Functions
        if module["functions"]:
            report += f"**Functions:** ({len(module['functions'])})\n\n"
            for func in module["functions"]:
                args_str = ", ".join(func["args"])
                report += f"- `{func['name']}({args_str})`\n"
            report += "\n"

        # Classes
        if module["classes"]:
            report += f"**Classes:** ({len(module['classes'])})\n\n"
            for cls in module["classes"]:
                if cls["bases"]:
                    bases_str = f" ({', '.join(cls['bases'])})"
                else:
                    bases_str = ""
                report += f"- `{cls['name']}{bases_str}`\n"

                if cls["methods"]:
                    for method in cls["methods"]:
                        report += f"  - `{method}()`\n"
            report += "\n"

        # Imports
        if module["imports"]:
            report += f"**Imports:** {', '.join(module['imports'])}\n\n"

        report += f"---\n\n"

    return report
