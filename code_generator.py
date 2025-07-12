import os
from typing import Dict, List, Any
from jinja2 import Environment, FileSystemLoader, Template
import re
from template_validator import TemplateValidator

class FlaskCodeGenerator:
    """Generates Flask application code from parsed RAML"""
    
    def __init__(self, app_name: str = "flask_api", api_version: str = "v1", 
                 include_auth: bool = True, include_cors: bool = True, generate_tests: bool = True):
        self.app_name = app_name
        self.api_version = api_version
        self.include_auth = include_auth
        self.include_cors = include_cors
        self.generate_tests = generate_tests
        self.validator = TemplateValidator()
        
        # Setup Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader('templates'),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        self.env.filters['snake_case'] = self._to_snake_case
        self.env.filters['pascal_case'] = self._to_pascal_case
        self.env.filters['camel_case'] = self._to_camel_case
        self.env.filters['extract_param'] = self._extract_uri_parameter
        
    def generate(self, parsed_raml: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate complete Flask application from parsed RAML
        
        Args:
            parsed_raml: Parsed RAML data
            
        Returns:
            Dictionary mapping file paths to their content
        """
        generated_files = {}
        
        # Extract resource information
        resources = self._process_resources(parsed_raml.get('resources', []))
        types = parsed_raml.get('types', {})
        
        # Generate application structure
        generated_files.update(self._generate_app_structure(parsed_raml, resources, types))
        generated_files.update(self._generate_models(resources, types))
        generated_files.update(self._generate_schemas(resources, types))
        generated_files.update(self._generate_services(resources))
        generated_files.update(self._generate_api_routes(resources, parsed_raml))
        generated_files.update(self._generate_config_files(parsed_raml))
        if self.generate_tests:
            generated_files.update(self._generate_tests(resources))
        generated_files.update(self._generate_readme(parsed_raml, resources))
        
        # Validate generated code for syntax errors
        is_valid, errors = self.validator.validate_generated_files(generated_files)
        if not is_valid:
            raise ValueError(f"Generated code contains syntax errors: {'; '.join(errors)}")
        
        return generated_files
    
    def _process_resources(self, resources: List[Dict]) -> Dict[str, Any]:
        """Process and organize resources for code generation"""
        processed = {}
        
        for resource in resources:
            # Extract resource name from URI
            uri_parts = [part for part in resource['uri'].strip('/').split('/') 
                        if part and not re.match(r'^\{.*\}$', part)]
            
            if uri_parts:
                resource_name = uri_parts[-1]
                if resource_name not in processed:
                    processed[resource_name] = {
                        'name': resource_name,
                        'endpoints': [],
                        'model_fields': set()
                    }
                
                # Add endpoint with relative URI (remove leading slash for blueprint)
                relative_uri = resource['uri'].lstrip('/')
                if relative_uri.startswith(f'{self.api_version}/'):
                    relative_uri = relative_uri[len(f'{self.api_version}/'):]
                endpoint = {
                    'uri': '/' + relative_uri if relative_uri else '/',
                    'methods': resource['methods'],
                    'description': resource.get('description', ''),
                    'uriParameters': resource.get('uriParameters', {})
                }
                processed[resource_name]['endpoints'].append(endpoint)
                
                # Extract model fields from request/response bodies
                for method in resource['methods']:
                    for body_data in method.get('body', {}).values():
                        if isinstance(body_data, dict) and 'properties' in body_data:
                            processed[resource_name]['model_fields'].update(
                                body_data['properties'].keys()
                            )
                    
                    for response_data in method.get('responses', {}).values():
                        for body_data in response_data.get('body', {}).values():
                            if isinstance(body_data, dict) and 'properties' in body_data:
                                processed[resource_name]['model_fields'].update(
                                    body_data['properties'].keys()
                                )
        
        return processed
    
    def _generate_app_structure(self, parsed_raml: Dict, resources: Dict, types: Dict) -> Dict[str, str]:
        """Generate main application structure files"""
        files = {}
        
        # app/__init__.py
        template = self.env.get_template('flask_app_init.py.j2')
        files['app/__init__.py'] = template.render(
            app_name=self.app_name,
            api_version=self.api_version,
            include_auth=self.include_auth,
            include_cors=self.include_cors,
            resources=list(resources.keys())
        )
        
        # app/config.py
        template = self.env.get_template('config.py.j2')
        files['app/config.py'] = template.render(
            app_name=self.app_name
        )
        
        # app/extensions/db.py
        template = self.env.get_template('extensions_db.py.j2')
        files['app/extensions/db.py'] = template.render()
        
        # app/extensions/__init__.py
        files['app/extensions/__init__.py'] = '# Flask extensions'
        
        # app/errors/handlers.py
        template = self.env.get_template('error_handlers.py.j2')
        files['app/errors/handlers.py'] = template.render()
        
        # app/errors/__init__.py
        files['app/errors/__init__.py'] = '# Error handlers'
        
        # app/utils/__init__.py
        files['app/utils/__init__.py'] = '# Utility functions'
        
        # wsgi.py
        template = self.env.get_template('wsgi.py.j2')
        files['wsgi.py'] = template.render(app_name=self.app_name)
        
        # requirements.txt
        template = self.env.get_template('requirements.txt.j2')
        files['requirements.txt'] = template.render(
            include_auth=self.include_auth,
            include_cors=self.include_cors
        )
        
        # README.md
        template = self.env.get_template('readme.md.j2')
        files['README.md'] = template.render(
            app_name=self.app_name,
            title=parsed_raml.get('title', 'API'),
            description=parsed_raml.get('description', ''),
            version=parsed_raml.get('version', '1.0'),
            api_version=self.api_version
        )
        
        return files
    
    def _generate_models(self, resources: Dict, types: Dict) -> Dict[str, str]:
        """Generate SQLAlchemy models"""
        files = {}
        
        # app/models/__init__.py
        model_imports = [f"from .{name} import {self._to_pascal_case(name)}" 
                        for name in resources.keys()]
        files['app/models/__init__.py'] = '\n'.join(model_imports) if model_imports else '# Models'
        
        # Generate individual model files
        template = self.env.get_template('model_clean.py.j2')
        for resource_name, resource_data in resources.items():
            class_name = self._to_pascal_case(resource_name)
            
            # Get fields from RAML types or infer from endpoints
            fields = []
            if resource_name in types:
                type_def = types[resource_name]
                for field_name, field_def in type_def.get('properties', {}).items():
                    fields.append({
                        'name': field_name,
                        'type': self._map_raml_type_to_sqlalchemy(field_def.get('type', 'string')),
                        'required': field_name in type_def.get('required', [])
                    })
            else:
                # Infer basic fields
                for field_name in resource_data['model_fields']:
                    fields.append({
                        'name': field_name,
                        'type': 'db.String(255)',
                        'required': False
                    })
            
            # Add default fields if none specified
            if not fields:
                fields = [
                    {'name': 'id', 'type': 'db.Integer', 'required': True, 'primary_key': True},
                    {'name': 'name', 'type': 'db.String(255)', 'required': True},
                    {'name': 'created_at', 'type': 'db.DateTime', 'required': False, 'default': 'datetime.utcnow'}
                ]
            
            files[f'app/models/{resource_name}.py'] = template.render(
                class_name=class_name,
                table_name=resource_name,
                fields=fields
            )
        
        return files
    
    def _generate_schemas(self, resources: Dict, types: Dict) -> Dict[str, str]:
        """Generate Marshmallow schemas"""
        files = {}
        
        # app/schemas/__init__.py
        schema_imports = [f"from .{name}_schema import {self._to_pascal_case(name)}Schema" 
                         for name in resources.keys()]
        files['app/schemas/__init__.py'] = '\n'.join(schema_imports) if schema_imports else '# Schemas'
        
        # Generate individual schema files
        template = self.env.get_template('schema.py.j2')
        for resource_name, resource_data in resources.items():
            class_name = self._to_pascal_case(resource_name)  # Remove Schema suffix here
            model_name = self._to_pascal_case(resource_name)
            
            files[f'app/schemas/{resource_name}_schema.py'] = template.render(
                class_name=class_name,
                model_name=model_name,
                resource_name=resource_name
            )
        
        return files
    
    def _generate_services(self, resources: Dict) -> Dict[str, str]:
        """Generate service layer files"""
        files = {}
        
        # app/services/__init__.py
        service_imports = [f"from .{name}_service import {self._to_pascal_case(name)}Service" 
                          for name in resources.keys()]
        files['app/services/__init__.py'] = '\n'.join(service_imports) if service_imports else '# Services'
        
        # Generate individual service files
        template = self.env.get_template('service.py.j2')
        for resource_name, resource_data in resources.items():
            class_name = f"{self._to_pascal_case(resource_name)}Service"
            model_name = self._to_pascal_case(resource_name)
            
            files[f'app/services/{resource_name}_service.py'] = template.render(
                class_name=class_name,
                model_name=model_name,
                resource_name=resource_name
            )
        
        return files
    
    def _generate_api_routes(self, resources: Dict, parsed_raml: Dict) -> Dict[str, str]:
        """Generate API route files"""
        files = {}
        
        # app/api/__init__.py
        template = self.env.get_template('api_init.py.j2')
        files['app/api/__init__.py'] = template.render(
            api_version=self.api_version,
            resources=list(resources.keys())
        )
        
        # app/api/v1/__init__.py (or other version)
        files[f'app/api/{self.api_version}/__init__.py'] = f'# API {self.api_version} routes'
        
        # Generate individual route files
        template = self.env.get_template('api_route_clean.py.j2')
        for resource_name, resource_data in resources.items():
            class_name = self._to_pascal_case(resource_name)
            
            files[f'app/api/{self.api_version}/{resource_name}.py'] = template.render(
                resource_name=resource_name,
                class_name=class_name,
                endpoints=resource_data['endpoints'],
                api_version=self.api_version
            )
        
        return files
    
    def _generate_config_files(self, parsed_raml: Dict) -> Dict[str, str]:
        """Generate configuration and setup files"""
        files = {}
        
        # .env (example)
        files['.env.example'] = """# Environment variables for local development
DATABASE_URL=sqlite:///app.db
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=jwt-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True
"""
        
        # .gitignore
        files['.gitignore'] = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Flask
instance/
.webassets-cache

# Environment variables
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log

# OS
.DS_Store
Thumbs.db
"""
        
        # run.py - Application entry point
        template = self.env.get_template('run.py.j2')
        files['run.py'] = template.render(
            app_name=self.app_name
        )
        
        # requirements.txt
        requirements = [
            "Flask>=2.3.0",
            "Flask-SQLAlchemy>=3.0.0",
            "marshmallow>=3.19.0",
            "flask-marshmallow>=0.15.0",
            "marshmallow-sqlalchemy>=0.29.0"
        ]
        
        if self.include_auth:
            requirements.append("Flask-JWT-Extended>=4.5.0")
        
        if self.include_cors:
            requirements.append("Flask-CORS>=4.0.0")
        
        # Always include Werkzeug for Flask compatibility
        requirements.append("Werkzeug>=2.3.0")
        
        # Add testing dependencies
        test_requirements = [
            "pytest>=7.0.0",
            "pytest-flask>=1.2.0",
            "pytest-cov>=4.0.0"
        ]
        
        files['requirements.txt'] = '\n'.join(requirements) + '\n'
        files['requirements-dev.txt'] = '\n'.join(requirements + test_requirements) + '\n'
        
        return files
    
    def _generate_tests(self, resources: Dict) -> Dict[str, str]:
        """Generate test files for Flask application"""
        files = {}
        
        # tests/__init__.py
        files['tests/__init__.py'] = '# Test package'
        
        # conftest.py - pytest configuration
        template = self.env.get_template('conftest.py.j2')
        files['tests/conftest.py'] = template.render(
            app_name=self.app_name
        )
        
        # pytest.ini - pytest configuration
        template = self.env.get_template('flask_pytest_ini.j2')
        files['pytest.ini'] = template.render()
        
        # Generate test files for each resource
        test_template = self.env.get_template('flask_test.py.j2')
        for resource_name, resource_data in resources.items():
            class_name = self._to_pascal_case(resource_name)
            
            files[f'tests/test_{resource_name}.py'] = test_template.render(
                resource_name=resource_name,
                class_name=class_name,
                endpoints=resource_data['endpoints'],
                api_version=self.api_version
            )
        
        return files
    
    def _generate_readme(self, parsed_raml: Dict, resources: Dict) -> Dict[str, str]:
        """Generate README file with setup instructions"""
        files = {}
        
        template = self.env.get_template('README.md.j2')
        files['README.md'] = template.render(
            app_name=self.app_name,
            api_version=self.api_version,
            include_auth=self.include_auth,
            include_cors=self.include_cors,
            resources=resources,
            title=parsed_raml.get('title', 'Generated API'),
            description=parsed_raml.get('description', 'API generated from RAML specification')
        )
        
        return files
    
    def _map_raml_type_to_sqlalchemy(self, raml_type: str) -> str:
        """Map RAML types to SQLAlchemy column types"""
        type_mapping = {
            'string': 'db.String(255)',
            'integer': 'db.Integer',
            'number': 'db.Float',
            'boolean': 'db.Boolean',
            'date': 'db.Date',
            'datetime': 'db.DateTime',
            'array': 'db.Text',  # JSON array
            'object': 'db.Text'  # JSON object
        }
        return type_mapping.get(raml_type.lower(), 'db.String(255)')
    
    def _to_snake_case(self, text: str) -> str:
        """Convert text to snake_case"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _to_pascal_case(self, text: str) -> str:
        """Convert text to PascalCase"""
        return ''.join(word.capitalize() for word in re.split(r'[_\-\s]+', text))
    
    def _to_camel_case(self, text: str) -> str:
        """Convert text to camelCase"""
        pascal = self._to_pascal_case(text)
        return pascal[0].lower() + pascal[1:] if pascal else ""
    
    def _extract_uri_parameter(self, uri: str) -> str:
        """Extract parameter name from URI pattern like /users/{investigation-id} -> investigation_id"""
        import re
        match = re.search(r'\{([^}]+)\}', uri)
        if match:
            param_name = match.group(1)
            # Convert hyphens to underscores for valid Python parameter names
            return param_name.replace('-', '_')
        return 'id'
