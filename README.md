# RAML to Flask API Generator

## Quick Start

1. Install dependencies:
```bash
pip install streamlit jinja2 pyyaml
```

2. Run the application:
```bash
streamlit run app.py --server.port 5000
```

3. Open your browser to: http://localhost:5000

## Project Structure

- `app.py` - Main Streamlit application
- `raml_parser.py` - RAML specification parser
- `code_generator.py` - Flask application generator  
- `client_generator.py` - Python client library generator
- `template_validator.py` - Code validation utilities
- `templates/` - Jinja2 templates for code generation

## Features

- Parse RAML 1.0 specifications
- Generate production-ready Flask REST APIs
- Create Python client libraries with pytest tests
- Support for batch processing multiple projects
- JWT authentication and CORS support
- Comprehensive error handling and validation

## Usage

1. Upload RAML files (single file, ZIP folder, or multiple ZIPs)
2. Configure generation options (auth, CORS, client generation)
3. Generate and download complete Flask applications and Python clients

The generated code follows best practices with proper project structure, 
models, schemas, services, and API routes.
