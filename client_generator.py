"""
Python API Client Generator for RAML specifications
Generates Python client libraries with pytest test suites
"""
import os
from typing import Dict, List, Any
from jinja2 import Environment, FileSystemLoader, select_autoescape


class PythonClientGenerator:
    """Generates Python API client libraries from parsed RAML"""
    
    def __init__(self, api_name: str = "api_client", include_auth: bool = True, generate_tests: bool = True):
        self.api_name = api_name
        self.include_auth = include_auth
        self.generate_tests = generate_tests
        self.env = Environment(
            loader=FileSystemLoader('templates'),
            autoescape=select_autoescape(['py']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self._setup_filters()
    
    def _setup_filters(self):
        """Setup custom Jinja2 filters for client generation"""
        self.env.filters['to_snake_case'] = self._to_snake_case
        self.env.filters['to_pascal_case'] = self._to_pascal_case
        self.env.filters['to_camel_case'] = self._to_camel_case
        self.env.filters['extract_path_params'] = self._extract_path_params
        self.env.filters['get_response_type'] = self._get_response_type
    
    def generate(self, parsed_raml: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate complete Python client library from parsed RAML
        
        Args:
            parsed_raml: Parsed RAML data
            
        Returns:
            Dictionary mapping file paths to their content
        """
        files = {}
        
        # Process resources and organize them
        resources = self._process_resources(parsed_raml.get('resources', []))
        types = parsed_raml.get('types', {})
        
        # Generate client library files
        files.update(self._generate_client_structure(parsed_raml, resources, types))
        files.update(self._generate_client_classes(resources, types))
        files.update(self._generate_models(types))
        if self.generate_tests:
            files.update(self._generate_tests(resources, types))
        files.update(self._generate_config_files(parsed_raml))
        files.update(self._generate_examples(resources))
        
        return files
    
    def _process_resources(self, resources: List[Dict]) -> Dict[str, Any]:
        """Process and organize resources for client generation"""
        processed = {}
        
        for resource in resources:
            resource_name = self._get_resource_name(resource['uri'])
            if resource_name not in processed:
                processed[resource_name] = {
                    'name': resource_name,
                    'uri': resource['uri'],
                    'methods': [],
                    'path_params': self._extract_path_params(resource['uri'])
                }
            
            for method in resource.get('methods', []):
                # Handle both dictionary and string method data
                if isinstance(method, dict):
                    method_name = method.get('method', 'GET').upper()
                    method_data = method
                else:
                    method_name = str(method).upper()
                    method_data = {}
                
                processed[resource_name]['methods'].append({
                    'method': method_name,
                    'description': method_data.get('description', ''),
                    'query_params': method_data.get('queryParameters', {}),
                    'body': method_data.get('body', {}),
                    'responses': method_data.get('responses', {}),
                    'uri': resource['uri']
                })
        
        return processed
    
    def _generate_client_structure(self, parsed_raml: Dict, resources: Dict, types: Dict) -> Dict[str, str]:
        """Generate main client structure files"""
        files = {}
        
        # Main __init__.py
        template = self.env.get_template('client_init.py.j2')
        files['__init__.py'] = template.render(
            api_name=self.api_name,
            resources=resources,
            include_auth=self.include_auth
        )
        
        # Base client class
        template = self.env.get_template('base_client.py.j2')
        files['base_client.py'] = template.render(
            api_name=self.api_name,
            base_uri=parsed_raml.get('baseUri', 'https://api.example.com'),
            version=parsed_raml.get('version', '1.0'),
            include_auth=self.include_auth
        )
        
        # Exceptions
        template = self.env.get_template('exceptions.py.j2')
        files['exceptions.py'] = template.render(api_name=self.api_name)
        
        return files
    
    def _generate_client_classes(self, resources: Dict, types: Dict) -> Dict[str, str]:
        """Generate API client classes for each resource"""
        files = {}
        template = self.env.get_template('resource_client_simple.py.j2')
        
        for resource_name, resource_data in resources.items():
            class_name = self._to_pascal_case(resource_name)
            
            # Debug: Check if methods exist
            if not resource_data.get('methods'):
                print(f"Warning: No methods found for resource {resource_name}")
                resource_data['methods'] = []
            
            try:
                files[f'{resource_name}_client.py'] = template.render(
                    resource_name=resource_name,
                    class_name=class_name,
                    resource_data=resource_data,
                    api_name=self.api_name,
                    include_auth=self.include_auth
                )
            except Exception as e:
                print(f"Error rendering template for {resource_name}: {e}")
                print(f"Resource data: {resource_data}")
                raise
        
        return files
    
    def _generate_models(self, types: Dict) -> Dict[str, str]:
        """Generate data model classes"""
        files = {}
        
        if not types:
            return files
        
        template = self.env.get_template('models.py.j2')
        files['models.py'] = template.render(
            types=types,
            api_name=self.api_name
        )
        
        return files
    
    def _generate_tests(self, resources: Dict, types: Dict) -> Dict[str, str]:
        """Generate pytest test suites"""
        files = {}
        
        # Test configuration
        template = self.env.get_template('test_config.py.j2')
        files['tests/__init__.py'] = ""
        files['tests/conftest.py'] = template.render(
            api_name=self.api_name,
            include_auth=self.include_auth
        )
        
        # Test for each resource
        template = self.env.get_template('test_resource.py.j2')
        for resource_name, resource_data in resources.items():
            class_name = self._to_pascal_case(resource_name)
            files[f'tests/test_{resource_name}.py'] = template.render(
                resource_name=resource_name,
                class_name=class_name,
                resource_data=resource_data,
                api_name=self.api_name
            )
        
        # Integration tests
        template = self.env.get_template('test_integration.py.j2')
        files['tests/test_integration.py'] = template.render(
            resources=resources,
            api_name=self.api_name
        )
        
        return files
    
    def _generate_config_files(self, parsed_raml: Dict) -> Dict[str, str]:
        """Generate configuration and setup files"""
        files = {}
        
        # setup.py
        template = self.env.get_template('setup.py.j2')
        files['setup.py'] = template.render(
            api_name=self.api_name,
            version=parsed_raml.get('version', '1.0.0'),
            description=parsed_raml.get('description', f'{self.api_name} Python Client'),
            title=parsed_raml.get('title', self.api_name)
        )
        
        # requirements.txt
        template = self.env.get_template('client_requirements.txt.j2')
        files['requirements.txt'] = template.render(include_auth=self.include_auth)
        
        # requirements-dev.txt
        template = self.env.get_template('client_requirements_dev.txt.j2')
        files['requirements-dev.txt'] = template.render()
        
        # pytest.ini
        template = self.env.get_template('pytest.ini.j2')
        files['pytest.ini'] = template.render(api_name=self.api_name)
        
        # .gitignore
        template = self.env.get_template('client_gitignore.j2')
        files['.gitignore'] = template.render()
        
        # README.md
        template = self.env.get_template('client_readme.md.j2')
        files['README.md'] = template.render(
            api_name=self.api_name,
            resources=resources,
            include_auth=self.include_auth,
            raml_data=parsed_raml
        )
        
        return files
    
    def _generate_examples(self, resources: Dict) -> Dict[str, str]:
        """Generate usage examples"""
        files = {}
        
        template = self.env.get_template('examples.py.j2')
        files['examples/basic_usage.py'] = template.render(
            resources=resources,
            api_name=self.api_name,
            include_auth=self.include_auth
        )
        
        files['examples/__init__.py'] = ""
        
        return files
    
    def _get_resource_name(self, uri: str) -> str:
        """Extract resource name from URI"""
        # Remove leading slash and extract the main resource
        parts = uri.strip('/').split('/')
        # Get the first non-parameter part
        for part in parts:
            if not part.startswith('{') and part:
                return self._to_snake_case(part)
        return "resource"
    
    def _extract_path_params(self, uri: str) -> List[str]:
        """Extract path parameters from URI"""
        import re
        params = re.findall(r'\{([^}]+)\}', uri)
        return [self._to_snake_case(param.replace('-', '_')) for param in params]
    
    def _get_response_type(self, responses: Dict) -> str:
        """Determine the expected response type"""
        if '200' in responses:
            return responses['200'].get('body', {}).get('application/json', {}).get('type', 'dict')
        return 'dict'
    
    def _to_snake_case(self, text: str) -> str:
        """Convert text to snake_case"""
        import re
        text = re.sub(r'[-\s]+', '_', text)
        text = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', text)
        return text.lower().strip('_')
    
    def _to_pascal_case(self, text: str) -> str:
        """Convert text to PascalCase"""
        words = self._to_snake_case(text).split('_')
        return ''.join(word.capitalize() for word in words if word)
    
    def _to_camel_case(self, text: str) -> str:
        """Convert text to camelCase"""
        pascal = self._to_pascal_case(text)
        return pascal[0].lower() + pascal[1:] if pascal else ""