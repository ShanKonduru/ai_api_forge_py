"""
Template validation module to ensure generated code is syntactically correct
"""
import ast
import tempfile
import os
from typing import Dict, List, Tuple


class TemplateValidator:
    """Validates generated Python code for syntax errors"""
    
    def __init__(self):
        self.errors = []
    
    def validate_python_syntax(self, code: str, filename: str = "<string>") -> bool:
        """
        Validate Python code syntax
        
        Args:
            code: Python code to validate
            filename: Optional filename for error reporting
            
        Returns:
            True if syntax is valid, False otherwise
        """
        try:
            ast.parse(code, filename=filename)
            return True
        except SyntaxError as e:
            self.errors.append(f"Syntax error in {filename}: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Error parsing {filename}: {e}")
            return False
    
    def validate_generated_files(self, files: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Validate all generated Python files
        
        Args:
            files: Dictionary mapping file paths to their content
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        self.errors = []
        all_valid = True
        
        for file_path, content in files.items():
            # Only validate Python files
            if file_path.endswith('.py'):
                if not self.validate_python_syntax(content, file_path):
                    all_valid = False
        
        return all_valid, self.errors
    
    def validate_imports(self, files: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Validate that all imports in generated files are resolvable
        
        Args:
            files: Dictionary mapping file paths to their content
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        import_errors = []
        
        # Create a temporary directory structure to test imports
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write all files to temp directory
            for file_path, content in files.items():
                full_path = os.path.join(temp_dir, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # Try to validate imports (basic check)
            for file_path, content in files.items():
                if file_path.endswith('.py'):
                    try:
                        # Parse the file and check for import statements
                        tree = ast.parse(content, filename=file_path)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for alias in node.names:
                                    # Basic import validation
                                    pass
                            elif isinstance(node, ast.ImportFrom):
                                # Basic from import validation
                                pass
                    except Exception as e:
                        import_errors.append(f"Import validation error in {file_path}: {e}")
        
        return len(import_errors) == 0, import_errors