import yaml
import re
from typing import Dict, List, Any, Optional
from yaml.constructor import ConstructorError

class RAMLParser:
    """Parser for RAML 1.0 specifications"""
    
    def __init__(self):
        self.parsed_data = {}
        self.project_directory = None
        self._setup_yaml_loader()
    
    def _setup_yaml_loader(self):
        """Setup YAML loader with custom constructors for RAML directives"""
        # Create a custom loader that handles RAML-specific tags
        class RAMLLoader(yaml.SafeLoader):
            pass
        
        def include_constructor(loader, node):
            """Handle !include directive by returning a placeholder"""
            if isinstance(node, yaml.ScalarNode):
                filename = loader.construct_scalar(node)
                # Return a placeholder that indicates this was an include
                return f"__INCLUDE__{filename}__"
            return None
        
        def type_constructor(loader, node):
            """Handle custom type constructors"""
            if isinstance(node, yaml.ScalarNode):
                return loader.construct_scalar(node)
            elif isinstance(node, yaml.MappingNode):
                return loader.construct_mapping(node)
            return None
        
        # Register constructors for RAML directives
        RAMLLoader.add_constructor('!include', include_constructor)
        RAMLLoader.add_constructor('!type', type_constructor)
        
        # Store the loader class for use in parsing
        self.loader_class = RAMLLoader
    
    def set_project_directory(self, directory: str):
        """Set the project directory for resolving includes"""
        self.project_directory = directory
        
    def parse(self, raml_content: str) -> Dict[str, Any]:
        """
        Parse RAML content and extract API structure
        
        Args:
            raml_content: Raw RAML file content
            
        Returns:
            Parsed RAML structure with resources, types, and metadata
        """
        try:
            # Parse YAML content using custom RAML loader
            data = yaml.load(raml_content, Loader=self.loader_class)
            
            if not isinstance(data, dict):
                raise ValueError("Invalid RAML format: Root element must be an object")
            
            # Extract basic information
            self.parsed_data = {
                'title': data.get('title', 'API'),
                'version': data.get('version', '1.0'),
                'baseUri': data.get('baseUri', '/api'),
                'description': data.get('description', ''),
                'mediaType': data.get('mediaType', 'application/json'),
                'protocols': data.get('protocols', ['HTTP', 'HTTPS']),
                'types': self._extract_types(data.get('types', {})),
                'traits': data.get('traits', {}),
                'securitySchemes': data.get('securitySchemes', {}),
                'resources': []
            }
            
            # Process any includes and resolve types
            self._process_includes(self.parsed_data)
            
            # Extract resources (endpoints)
            self._extract_resources(data, '')
            
            return self.parsed_data
            
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML syntax: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing RAML: {str(e)}")
    
    def _process_includes(self, data: Dict[str, Any]):
        """Process !include directives and resolve them"""
        def process_dict(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, str) and value.startswith("__INCLUDE__"):
                        # Handle include - try to resolve the file
                        filename = value.replace("__INCLUDE__", "").replace("__", "")
                        resolved_content = self._resolve_include(filename)
                        if resolved_content is not None:
                            obj[key] = resolved_content
                        else:
                            # Create a placeholder if we can't resolve
                            if filename.endswith('.raml') or 'datatype' in filename:
                                obj[key] = {
                                    'type': 'object',
                                    'properties': {},
                                    'description': f'Included from {filename}'
                                }
                            else:
                                obj[key] = 'string'  # Default to string type
                    else:
                        process_dict(value)
            elif isinstance(obj, list):
                for item in obj:
                    process_dict(item)
        
        process_dict(data)
    
    def _resolve_include(self, filename: str) -> Any:
        """Resolve an included file and return its content"""
        if not self.project_directory:
            return None
        
        import os
        
        # Try to find the file in the project directory
        possible_paths = [
            os.path.join(self.project_directory, filename),
            os.path.join(self.project_directory, filename + '.raml'),
            os.path.join(self.project_directory, 'datatypes', filename),
            os.path.join(self.project_directory, 'datatypes', filename + '.raml'),
            os.path.join(self.project_directory, 'types', filename),
            os.path.join(self.project_directory, 'types', filename + '.raml'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Clean up content - replace tabs with spaces for YAML compatibility
                    content = content.expandtabs(2)
                    
                    # Parse the included file
                    if path.endswith(('.raml', '.yaml', '.yml')):
                        try:
                            included_data = yaml.load(content, Loader=self.loader_class)
                            return included_data
                        except yaml.YAMLError as yaml_err:
                            # If YAML parsing fails, try to extract just the type information
                            lines = content.strip().split('\n')
                            if lines and not lines[0].startswith('#'):
                                # Try to parse as a simple type definition
                                try:
                                    simple_type = yaml.safe_load(content)
                                    return simple_type
                                except:
                                    # Last resort - create a basic object type
                                    return {
                                        'type': 'object',
                                        'description': f'Included from {os.path.basename(path)} (parsing error: {str(yaml_err)})'
                                    }
                            return content
                    else:
                        # For other files, return as string
                        return content
                        
                except Exception as e:
                    print(f"Error reading included file {path}: {e}")
                    continue
        
        return None
    
    def _extract_types(self, types_data: Dict) -> Dict[str, Any]:
        """Extract and process RAML types"""
        processed_types = {}
        
        for type_name, type_def in types_data.items():
            if isinstance(type_def, dict):
                processed_types[type_name] = {
                    'type': type_def.get('type', 'object'),
                    'properties': type_def.get('properties', {}),
                    'required': type_def.get('required', []),
                    'description': type_def.get('description', ''),
                    'example': type_def.get('example', {})
                }
            else:
                # Simple type definition
                processed_types[type_name] = {
                    'type': type_def,
                    'properties': {},
                    'required': [],
                    'description': '',
                    'example': {}
                }
        
        return processed_types
    
    def _extract_resources(self, data: Dict, parent_uri: str = ''):
        """Recursively extract resources and their methods"""
        for key, value in data.items():
            if key.startswith('/'):
                # This is a resource
                resource_uri = parent_uri + key
                resource = {
                    'uri': resource_uri,
                    'displayName': value.get('displayName', key),
                    'description': value.get('description', ''),
                    'methods': [],
                    'uriParameters': value.get('uriParameters', {})
                }
                
                # Extract HTTP methods
                for method_key, method_value in value.items():
                    if method_key.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
                        method = self._extract_method(method_key.upper(), method_value)
                        resource['methods'].append(method)
                
                self.parsed_data['resources'].append(resource)
                
                # Recursively process nested resources
                self._extract_resources(value, resource_uri)
    
    def _extract_method(self, method_name: str, method_data: Dict) -> Dict[str, Any]:
        """Extract method details"""
        method = {
            'method': method_name,
            'description': method_data.get('description', ''),
            'displayName': method_data.get('displayName', method_name),
            'queryParameters': method_data.get('queryParameters', {}),
            'headers': method_data.get('headers', {}),
            'body': self._extract_body(method_data.get('body', {})),
            'responses': self._extract_responses(method_data.get('responses', {})),
            'securedBy': method_data.get('securedBy', []),
            'is': method_data.get('is', [])  # traits
        }
        
        return method
    
    def _extract_body(self, body_data: Dict) -> Dict[str, Any]:
        """Extract request body information"""
        if not body_data:
            return {}
        
        body = {}
        for media_type, body_spec in body_data.items():
            if isinstance(body_spec, dict):
                body[media_type] = {
                    'type': body_spec.get('type', 'object'),
                    'properties': body_spec.get('properties', {}),
                    'required': body_spec.get('required', []),
                    'example': body_spec.get('example', {}),
                    'schema': body_spec.get('schema', '')
                }
            else:
                body[media_type] = {'type': body_spec}
        
        return body
    
    def _extract_responses(self, responses_data: Dict) -> Dict[str, Any]:
        """Extract response information"""
        responses = {}
        
        for status_code, response_data in responses_data.items():
            if isinstance(response_data, dict):
                responses[str(status_code)] = {
                    'description': response_data.get('description', ''),
                    'headers': response_data.get('headers', {}),
                    'body': self._extract_body(response_data.get('body', {}))
                }
            else:
                responses[str(status_code)] = {
                    'description': response_data,
                    'headers': {},
                    'body': {}
                }
        
        return responses
    
    def get_resource_names(self) -> List[str]:
        """Get list of resource names for model generation"""
        resource_names = set()
        
        for resource in self.parsed_data.get('resources', []):
            # Extract resource name from URI
            uri_parts = resource['uri'].strip('/').split('/')
            for part in uri_parts:
                # Remove URI parameters (e.g., {id})
                clean_part = re.sub(r'\{.*?\}', '', part)
                if clean_part and not clean_part.isdigit():
                    resource_names.add(clean_part.capitalize())
        
        return list(resource_names)
    
    def get_data_types(self) -> Dict[str, Any]:
        """Get all data types defined in RAML"""
        return self.parsed_data.get('types', {})
