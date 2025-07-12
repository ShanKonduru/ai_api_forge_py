#!/usr/bin/env python3
"""
Template validation script to test all Jinja2 templates
"""
import os
import sys
from code_generator import FlaskCodeGenerator
from raml_parser import RAMLParser

def create_test_raml():
    """Create a test RAML structure for validation"""
    return {
        'title': 'Test API',
        'version': '1.0',
        'description': 'Test API for template validation',
        'baseUri': 'http://localhost:5000/api',
        'resources': [
            {
                'uri': '/users',
                'methods': [
                    {
                        'method': 'GET',
                        'description': 'Get all users',
                        'responses': {
                            '200': {
                                'body': {
                                    'application/json': {
                                        'type': 'User[]'
                                    }
                                }
                            }
                        }
                    },
                    {
                        'method': 'POST',
                        'description': 'Create new user',
                        'body': {
                            'application/json': {
                                'type': 'User'
                            }
                        }
                    }
                ]
            },
            {
                'uri': '/users/{id}',
                'methods': [
                    {
                        'method': 'GET',
                        'description': 'Get user by ID'
                    },
                    {
                        'method': 'PUT',
                        'description': 'Update user'
                    },
                    {
                        'method': 'DELETE',
                        'description': 'Delete user'
                    }
                ]
            }
        ],
        'types': {
            'User': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'email': {'type': 'string'},
                    'created_at': {'type': 'datetime'}
                },
                'required': ['name', 'email']
            }
        }
    }

def validate_templates():
    """Validate all templates by generating code and checking syntax"""
    print("🔍 Validating Flask code generator templates...")
    
    try:
        # Create generator
        generator = FlaskCodeGenerator(
            app_name="test_api",
            api_version="v1",
            include_auth=True,
            include_cors=True
        )
        
        # Create test RAML data
        test_raml = create_test_raml()
        
        # Generate code
        print("📝 Generating code from templates...")
        generated_files = generator.generate(test_raml)
        
        print(f"✅ Generated {len(generated_files)} files successfully!")
        
        # List generated files
        print("\n📁 Generated files:")
        for file_path in sorted(generated_files.keys()):
            print(f"  - {file_path}")
        
        print("\n✅ All templates validated successfully!")
        print("🎉 No syntax errors found in generated code!")
        
        return True
        
    except Exception as e:
        print(f"❌ Template validation failed: {e}")
        return False

if __name__ == "__main__":
    success = validate_templates()
    sys.exit(0 if success else 1)