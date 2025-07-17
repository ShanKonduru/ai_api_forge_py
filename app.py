import streamlit as st
import yaml
import zipfile
import io
import os
import tempfile
import shutil
from pathlib import Path
from raml_parser import RAMLParser
from code_generator import FlaskCodeGenerator
from client_generator import PythonClientGenerator

def main():
    st.set_page_config(
        page_title="API Forge - RAML to Flask Generator",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state for wizard
    if 'wizard_step' not in st.session_state:
        st.session_state.wizard_step = 1
    if 'projects_data' not in st.session_state:
        st.session_state.projects_data = []
    if 'generated_files' not in st.session_state:
        st.session_state.generated_files = {}
    
    # Add navigation sidebar
    with st.sidebar:
        # Display the logo
        try:
            st.image("assets/api_forge_logo.svg", width=150)
        except:
            # Fallback if SVG file doesn't exist
            st.markdown("""
            <div style="width: 150px; height: 80px; background: linear-gradient(135deg, #2E86AB 0%, #4A90E2 100%); 
                        border-radius: 8px; display: flex; align-items: center; justify-content: center; 
                        color: white; font-weight: bold; font-size: 16px; margin-bottom: 1rem;">
                ⚡ API FORGE
            </div>
            """, unsafe_allow_html=True)
        st.markdown("---")
        # Determine current page index based on session state
        page_options = ["🏠 Home", "📖 About", "🛠️ API Forge - API Generator", "📚 Documentation"]
        
        # Set default or get from session state
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "🛠️ API Forge - API Generator"
        
        # Find the index of current page
        try:
            current_index = page_options.index(st.session_state.current_page)
        except ValueError:
            current_index = 2  # Default to API Generator
        
        page = st.selectbox(
            "Navigation",
            page_options,
            index=current_index,
            key="nav_selectbox"
        )
        
        # Update session state when selectbox changes
        if page != st.session_state.current_page:
            st.session_state.current_page = page
            st.rerun()
        
        st.markdown("---")
        st.markdown("**Quick Links**")
        
        # Documentation internal navigation
        if st.button("📚 Documentation", use_container_width=True):
            st.session_state.current_page = "📚 Documentation"
            st.rerun()
            
        # Support/Contact internal navigation
        if st.button("🆘 Support", use_container_width=True):
            st.session_state.current_page = "📖 About"
            st.rerun()
            
        # About internal navigation
        if st.button("📖 About", use_container_width=True):
            st.session_state.current_page = "📖 About"
            st.rerun()
    
    # Main content based on current page
    current_page = st.session_state.current_page
    if current_page == "📖 About":
        show_about_page()
    elif current_page == "📚 Documentation":
        show_documentation_page()
    elif current_page == "🏠 Home":
        show_home_page()
    else:  # API Generator
        show_generator_page()

def show_about_page():
    """Display the about page"""
    st.title("📖 About API Forge")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## Welcome to API Forge
        
        **API Forge** is a comprehensive tool for transforming RAML specifications into production-ready Flask REST APIs with complete Python client libraries. Built with modern development practices in mind, it bridges the gap between API design and implementation.
        
        ### 🎯 Mission
        To simplify and accelerate API development by automatically generating high-quality, production-ready code from RAML specifications.
        
        ### ✨ Key Features
        - **Complete Flask Applications**: Generate full-featured REST APIs with proper architecture
        - **Python Client Libraries**: Automatic client generation with pytest test suites
        - **Batch Processing**: Handle multiple projects simultaneously
        - **Production Ready**: Includes authentication, CORS, validation, and error handling
        - **Modern Stack**: Built with Flask, SQLAlchemy, Marshmallow, and pytest
        
        ### 🏗️ Architecture
        The system uses a modular architecture with:
        - **RAML Parser**: Intelligent parsing with include resolution
        - **Code Generator**: Template-based Flask application generation
        - **Client Generator**: Comprehensive Python client library creation
        - **Template Engine**: 30+ Jinja2 templates for clean code output
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Project Stats
        - **Languages**: Python, Jinja2
        - **Templates**: 32 files
        - **Code Lines**: 2000+
        - **Test Coverage**: Comprehensive
        
        ### 🛠️ Built With
        - Streamlit
        - Flask
        - SQLAlchemy
        - Marshmallow
        - pytest
        - Jinja2
        - PyYAML
        """)
    
    st.markdown("---")
    
    # Developer section
    st.subheader("👨‍💻 About RAVI BHUSHAN KONDURU (SHAN KONDURU)")
    dev_col1, dev_col2 = st.columns([1, 3])
    
    with dev_col1:
        # Display Shan's professional avatar
        try:
            st.image("assets/shan_konduru_avatar.svg", width=150)
        except:
            # Fallback if SVG file doesn't exist
            st.markdown("""
            <div style="width: 150px; height: 150px; background: linear-gradient(135deg, #2C3E50 0%, #4A90E2 100%); 
                        border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                        color: white; font-weight: bold; font-size: 16px; text-align: center;">
                Enterprise<br/>Architect
            </div>
            """, unsafe_allow_html=True)
    
    with dev_col2:
        st.markdown("""
        **Ravi Bhushan Konduru (Shan Konduru)**  
        *Enterprise Test Automation Architect*
        
        Ravi Bhushan Konduru, also known as Shan Konduru, is a highly accomplished Enterprise Test Automation Architect with **26 years** of extensive experience in software design, development, and testing across diverse technology landscapes. His profound expertise spans client/server, web-based enterprise, cloud-native (microservices), and REST Services applications.

        With a remarkable **12-year tenure at Coforge/Cigniti**, Shan has demonstrated unparalleled proficiency in product design, development, and testing within critical domains such as Railway, Transportation, Real Estate, Digital Asset Management, Finance, and Healthcare.

        A true leader in his field, Shan excels in Test Automation Framework Conceptualization, Design & Development, underpinned by a strong foundational knowledge in Object-Oriented Programming Concepts (OOPS). He is adept in a wide array of modern development methodologies, including Waterfall, Scrum, Agile, and SAFe, and possesses significant experience with cutting-edge approaches like XP, TDD, ATDD, DevOps, CI/CD Systems, Pair Programming, and Vibe coding.
        
        **Location:** Calgary, AB, Canada
        """)
    
    st.markdown("---")
    
    # Certifications section
    st.subheader("🏆 Professional Certifications")
    st.markdown("""
    Shan is committed to continuous learning and holds several prestigious certifications:
    
    - **AI Spark** (Apr 2025)
    - **Gremlin Certified Chaos Engineering Professional (GCCE Pro)**
    - **Gremlin Certified Chaos Engineering Practitioner (GCCEP)**
    - **Certified Scrum Professional (CSP)**
    - **SAFe Agilist (SA)**
    - **SAFe Program Consultant (SPC)**
    """)
    
    st.markdown("---")
    
    # Professional statement
    st.subheader("🎯 Professional Vision")
    st.info("""
    Based in Calgary, AB, Canada, Shan Konduru is dedicated to driving innovation and excellence in enterprise test automation, ensuring robust, scalable, and efficient software solutions.
    """)
    
    # Contact section
    st.subheader("📬 Get In Touch")
    contact_col1, contact_col2 = st.columns(2)
    
    with contact_col1:
        st.markdown("""
        **🐙 GitHub**  
        [github.com/ShanKonduru](https://github.com/ShanKonduru)
        
        **📘 Facebook**  
        [facebook.com/shan.konduru](https://www.facebook.com/shan.konduru/)
        """)
    
    with contact_col2:
        st.markdown("""
        **🐦 X (Twitter)**  
        [x.com/ShanKonduru](https://x.com/ShanKonduru)
        
        **💼 LinkedIn**  
        [linkedin.com/in/shankonduru](https://www.linkedin.com/in/shankonduru/)
        """)

def show_documentation_page():
    """Display the documentation page"""
    st.title("📚 Documentation")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🚀 Quick Start", "📝 RAML Guide", "🔧 Advanced", "❓ FAQ"])
    
    with tab1:
        st.markdown("""
        ## Quick Start Guide
        
        ### 1. Upload Your RAML
        - Choose single file, ZIP folder, or multiple projects
        - Supports RAML 1.0 specifications
        - Handles include directives automatically
        
        ### 2. Configure Generation
        - **JWT Authentication**: Add secure token-based auth
        - **CORS Support**: Enable cross-origin requests
        - **Python Client**: Generate client libraries with tests
        
        ### 3. Generate & Download
        - Complete Flask applications with proper structure
        - SQLAlchemy models and Marshmallow schemas
        - Service layer and API routes
        - Python client libraries with pytest suites
        
        ### 4. Deploy & Use
        ```bash
        # Extract and install
        pip install -r requirements.txt
        
        # Run Flask app
        python run.py
        
        # Run tests
        pytest
        ```
        """)
    
    with tab2:
        st.markdown("""
        ## RAML Specification Guide
        
        ### Supported Features
        - ✅ Resources and nested resources
        - ✅ HTTP methods (GET, POST, PUT, DELETE, PATCH)
        - ✅ URI parameters and query parameters
        - ✅ Request/response bodies
        - ✅ Data types and schemas
        - ✅ Security schemes
        - ✅ Include directives
        
        ### Example RAML Structure
        ```yaml
        #%RAML 1.0
        title: My API
        version: v1
        baseUri: https://api.example.com
        
        /users:
          get:
            description: Get all users
            responses:
              200:
                body:
                  application/json:
                    type: User[]
          post:
            description: Create user
            body:
              application/json:
                type: User
        
        types:
          User:
            type: object
            properties:
              id: integer
              name: string
              email: string
        ```
        """)
    
    with tab3:
        st.markdown("""
        ## Advanced Features
        
        ### Batch Processing
        - Upload multiple ZIP files simultaneously
        - Process up to 10 projects at once
        - Organized output with separate folders
        
        ### Custom Templates
        - 32 Jinja2 templates for code generation
        - Customizable naming conventions
        - Extensible architecture
        
        ### Code Quality
        - Automatic syntax validation
        - PEP 8 compliant output
        - Comprehensive error handling
        - Type hints throughout
        
        ### Testing
        - pytest test suites for all generated code
        - Mock-based unit tests
        - Integration test examples
        - Coverage reporting setup
        """)
    
    with tab4:
        st.markdown("""
        ## Frequently Asked Questions
        
        **Q: What RAML versions are supported?**  
        A: Currently supports RAML 1.0. RAML 0.8 support is planned.
        
        **Q: Can I customize the generated code?**  
        A: Yes! The templates are fully customizable and the code is designed to be extended.
        
        **Q: How do I handle authentication?**  
        A: Enable JWT authentication in the configuration. The generated code includes complete auth setup.
        
        **Q: What about database migrations?**  
        A: Generated Flask apps include Alembic configuration for database migrations.
        
        **Q: Can I contribute to the project?**  
        A: Absolutely! The project is open source and contributions are welcome.
        
        **Q: How do I report bugs?**  
        A: Create an issue in the GitHub repository with details about the problem.
        """)

def show_home_page():
    """Display the home page"""
    st.title("⚡ Welcome to API Forge")
    
    # Hero section
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; margin-bottom: 2rem;">
        <h2>Transform RAML Specs into Production-Ready APIs</h2>
        <p style="font-size: 1.2rem; margin-bottom: 1rem;">Generate complete Flask applications and Python client libraries from your RAML specifications</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features grid
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🚀 **Flask Applications**
        - Complete REST API structure
        - SQLAlchemy models
        - Marshmallow schemas
        - Authentication & CORS
        """)
    
    with col2:
        st.markdown("""
        ### 🐍 **Python Clients**
        - Requests-based API clients
        - Type hints & error handling
        - Comprehensive test suites
        - Ready-to-install packages
        """)
    
    with col3:
        st.markdown("""
        ### ⚙️ **Batch Processing**
        - Multiple projects at once
        - ZIP file support
        - Organized output
        - Progress tracking
        """)
    
    # Call to action
    st.markdown("---")
    st.markdown("### Ready to get started?")
    
    if st.button("🛠️ Go to API Forge - API Generator", type="primary", use_container_width=True):
        st.session_state.current_page = "🛠️ API Forge - API Generator"
        st.rerun()

def show_generator_page():
    """Display the main generator interface"""
    st.title("🛠️ API Forge - API Generator")
    st.markdown("Transform your RAML specifications into production-ready Flask REST APIs with Python client libraries")
    

    
    # Wizard progress bar
    progress_col1, progress_col2, progress_col3 = st.columns(3)
    with progress_col1:
        if st.session_state.wizard_step >= 1:
            st.success("**Step 1: Upload Files** ✅" if st.session_state.wizard_step > 1 else "**Step 1: Upload Files** 📁")
        else:
            st.info("**Step 1: Upload Files** 📁")
    with progress_col2:
        if st.session_state.wizard_step >= 2:
            st.success("**Step 2: Generate Code** ✅" if st.session_state.wizard_step > 2 else "**Step 2: Generate Code** ⚙️")
        else:
            st.info("**Step 2: Generate Code** ⚙️")
    with progress_col3:
        if st.session_state.wizard_step >= 3:
            st.success("**Step 3: Download** 📥")
        else:
            st.info("**Step 3: Download** 📥")
    
    st.divider()
    
    # Configuration at the top
    col_config1, col_config2, col_config3, col_config4 = st.columns(4)
    with col_config1:
        include_auth = st.checkbox("Include JWT Authentication", value=True)
    with col_config2:
        include_cors = st.checkbox("Include CORS Support", value=True)
    with col_config3:
        generate_client = st.checkbox("Generate Python Client", value=True, help="Generate Python client library with pytest tests")
    with col_config4:
        generate_tests = st.checkbox("Generate Pytest Tests", value=True, help="Generate pytest test suites for Flask APIs")
    
    # Set default values
    api_version = "v1"
    
    st.divider()
    
    # Step 1: Upload Files
    if st.session_state.wizard_step == 1:
        st.header("📁 Step 1: Upload RAML Projects")
        
        # Upload options
        upload_option = st.radio(
            "Choose upload method:",
            ["Single RAML File", "RAML Project Folder (ZIP)", "Multiple RAML Projects (Multiple ZIPs)"],
            help="Single file, one ZIP folder, or multiple ZIP files for batch processing"
        )
        
        if upload_option == "Single RAML File":
            uploaded_file = st.file_uploader(
                "Choose a RAML file",
                type=['raml', 'yaml', 'yml'],
                help="Upload your RAML 1.0 specification file"
            )
            uploaded_folders = None
        elif upload_option == "RAML Project Folder (ZIP)":
            uploaded_file = None
            uploaded_folders = st.file_uploader(
                "Choose a ZIP file containing your RAML project",
                type=None,  # Accept all file types
                help="Upload a ZIP file containing your RAML file and all referenced files",
                accept_multiple_files=False
            )
            # Convert single file to list for consistent processing
            if uploaded_folders:
                uploaded_folders = [uploaded_folders]
        else:  # Multiple RAML Projects (Multiple ZIPs)
            uploaded_file = None
            uploaded_folders = st.file_uploader(
                "Choose multiple ZIP files containing your RAML projects",
                type=None,  # Accept all file types
                accept_multiple_files=True,
                help="Upload multiple ZIP files to generate Flask apps for all your RAML projects at once"
            )
        
        # Use session state that was initialized at the top
        projects_data = st.session_state.projects_data
        
        if uploaded_file is not None or (uploaded_folders is not None and len(uploaded_folders) > 0):
            try:
                # Validate ZIP files if in ZIP upload mode
                if uploaded_folders is not None and len(uploaded_folders) > 0:
                    for folder in uploaded_folders:
                        if not folder.name.lower().endswith('.zip'):
                            st.error(f"❌ File '{folder.name}' is not a ZIP file. Please upload only ZIP files.")
                            st.stop()
                
                if uploaded_file is not None:
                    # Clear previous data and add single file
                    st.session_state.projects_data = []
                    
                    # Single file upload
                    raml_content = uploaded_file.read().decode('utf-8')
                    
                    # Auto-set app name based on uploaded file name
                    uploaded_file_name = uploaded_file.name
                    file_name_without_ext = os.path.splitext(uploaded_file_name)[0]
                    auto_app_name = f"{file_name_without_ext}-dummy"
                    st.info(f"📄 Uploaded file: **{uploaded_file_name}** → App name set to: **{auto_app_name}**")
                    
                    st.session_state.projects_data.append({
                        'name': auto_app_name,
                        'raml_content': raml_content,
                        'temp_dir': None
                    })
                    projects_data = st.session_state.projects_data
                    
                elif uploaded_folders is not None and len(uploaded_folders) > 0:
                    # Clear previous data for new uploads
                    st.session_state.projects_data = []
                    st.info(f"📦 Processing {len(uploaded_folders)} ZIP file(s)...")
                    
                    for idx, uploaded_folder in enumerate(uploaded_folders):
                        st.write(f"**Processing ZIP {idx + 1}/{len(uploaded_folders)}: {uploaded_folder.name}**")
                        
                        # Folder upload - extract and process
                        temp_dir = tempfile.mkdtemp()
                        try:
                            # Extract ZIP file
                            with zipfile.ZipFile(uploaded_folder, 'r') as zip_ref:
                                zip_ref.extractall(temp_dir)
                            
                            # Determine the actual project directory
                            extracted_items = os.listdir(temp_dir)
                            if len(extracted_items) == 1 and os.path.isdir(os.path.join(temp_dir, extracted_items[0])):
                                # Single root folder
                                actual_project_dir = os.path.join(temp_dir, extracted_items[0])
                            else:
                                # Multiple items or files at root
                                actual_project_dir = temp_dir
                            
                            # Find the main RAML file
                            raml_files = []
                            for root, dirs, files in os.walk(actual_project_dir):
                                for file in files:
                                    if file.endswith(('.raml', '.yaml', '.yml')):
                                        raml_files.append(os.path.join(root, file))
                            
                            if not raml_files:
                                st.warning(f"❌ No RAML files found in ZIP: {uploaded_folder.name}")
                                continue
                            
                            # Use the first RAML file found (for batch processing)
                            main_raml_path = raml_files[0]
                            
                            # Read the main RAML file
                            with open(main_raml_path, 'r', encoding='utf-8') as f:
                                raml_content = f.read()
                            
                            # Auto-set app name based on RAML file name
                            raml_file_name = os.path.basename(main_raml_path)
                            raml_name_without_ext = os.path.splitext(raml_file_name)[0]
                            auto_app_name = f"{raml_name_without_ext}-dummy"
                            
                            # Set up parser with project directory for include resolution
                            parser = RAMLParser()
                            parser.set_project_directory(actual_project_dir)
                            parsed_raml = parser.parse(raml_content)
                            
                            st.session_state.projects_data.append({
                                'name': auto_app_name,
                                'raml_content': raml_content,
                                'parsed_raml': parsed_raml,
                                'temp_dir': actual_project_dir,
                                'zip_name': uploaded_folder.name
                            })
                            
                            st.success(f"✅ {uploaded_folder.name} → {auto_app_name}")
                            
                        except Exception as e:
                            st.error(f"❌ Error processing {uploaded_folder.name}: {str(e)}")
                        finally:
                            # Keep temp_dir for now, clean up later
                            pass
                # Parse single file projects
                if uploaded_file is not None and st.session_state.projects_data:
                    parser = RAMLParser()
                    parsed_raml = parser.parse(st.session_state.projects_data[0]['raml_content'])
                    st.session_state.projects_data[0]['parsed_raml'] = parsed_raml
                
                # Update local variable from session state
                projects_data = st.session_state.projects_data
                
                # Display summary for all projects
                if projects_data:
                    st.success(f"✅ {len(projects_data)} project(s) parsed successfully!")
                    st.write("")
                    
                    # Display projects summary
                    st.subheader("📊 Projects Summary")
                    for idx, project in enumerate(projects_data):
                        parsed_raml = project.get('parsed_raml', {})
                        total_endpoints = len(parsed_raml.get('resources', []))
                        total_methods = sum(len(resource.get('methods', [])) for resource in parsed_raml.get('resources', []))
                        
                        with st.expander(f"Project {idx + 1}: {project['name']}", expanded=(len(projects_data) == 1)):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Endpoints", total_endpoints)
                            with col2:
                                st.metric("Methods", total_methods)
                            
                            # Show endpoints overview
                            if parsed_raml.get('resources'):
                                st.write("**Endpoints:**")
                                for resource in parsed_raml['resources']:
                                    methods_str = ", ".join([m['method'].upper() for m in resource.get('methods', [])])
                                    st.write(f"• `{resource['uri']}` - {methods_str}")
                    
                    # Next step button
                    st.write("")
                    if st.button("➡️ Continue to Code Generation", type="primary", use_container_width=True):
                        st.session_state.wizard_step = 2
                        st.rerun()
                
            except Exception as e:
                error_msg = str(e)
                if "!include" in error_msg:
                    st.error("❌ This RAML file contains !include directives. The generator now supports basic include handling, but external files won't be loaded. The generated code will use placeholder types for included definitions.")
                    st.info("💡 For best results, try uploading a self-contained RAML file without external includes, or ensure all type definitions are inline.")
                else:
                    st.error(f"❌ Error parsing RAML file: {error_msg}")
    
    # Step 2: Generate Code
    elif st.session_state.wizard_step == 2:
        st.header("⚙️ Step 2: Generate Flask Applications")
        
        if len(st.session_state.projects_data) > 0:
            st.info(f"✅ {len(st.session_state.projects_data)} project(s) ready for code generation!")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("🚀 Generate Flask APIs & Python Clients", type="primary", use_container_width=True):
                    try:
                        all_generated_files = {}
                        
                        with st.spinner(f"Generating Flask APIs and Python clients for {len(st.session_state.projects_data)} project(s)..."):
                            for idx, project in enumerate(st.session_state.projects_data):
                                st.write(f"Generating app {idx + 1}/{len(st.session_state.projects_data)}: {project['name']}")
                                
                                # Generate Flask code
                                generator = FlaskCodeGenerator(
                                    app_name=project['name'],
                                    api_version=api_version,
                                    include_auth=include_auth,
                                    include_cors=include_cors,
                                    generate_tests=generate_tests
                                )
                                
                                generated_files = generator.generate(project['parsed_raml'])
                                
                                # Add Flask project files under project directory
                                for file_path, content in generated_files.items():
                                    all_generated_files[f"{project['name']}-flask/{file_path}"] = content
                                
                                # Generate Python client if requested
                                if generate_client:
                                    st.write(f"  → Generating Python client for {project['name']}")
                                    try:
                                        client_generator = PythonClientGenerator(
                                            api_name=f"{project['name']}_client",
                                            include_auth=include_auth,
                                            generate_tests=generate_tests
                                        )
                                        
                                        # Debug: Show what's being passed to client generator
                                        resources_count = len(project['parsed_raml'].get('resources', []))
                                        st.write(f"    • Found {resources_count} resources in RAML")
                                        
                                        client_files = client_generator.generate(project['parsed_raml'])
                                        
                                        st.write(f"    • Generated {len(client_files)} client files")
                                        
                                        # Add client files under client directory
                                        for file_path, content in client_files.items():
                                            all_generated_files[f"{project['name']}-client/{file_path}"] = content
                                    except Exception as e:
                                        st.error(f"Error generating client for {project['name']}: {str(e)}")
                                        # Continue with other projects even if one fails
                                        continue
                            
                            st.success(f"✅ Generated Flask APIs{' and Python clients' if generate_client else ''} for {len(st.session_state.projects_data)} project(s)!")
                            
                            # Store generated files in session state
                            st.session_state.generated_files = all_generated_files
                            st.session_state.wizard_step = 3
                            st.rerun()
                            
                    except Exception as e:
                        import traceback
                        st.error(f"❌ Error generating code: {str(e)}")
                        with st.expander("🔍 Debug Details"):
                            st.text(traceback.format_exc())
                            st.write("**Parsed RAML structure:**")
                            for i, project in enumerate(st.session_state.projects_data):
                                st.write(f"Project {i+1}: {project['name']}")
                                st.write(f"  Resources: {len(project.get('parsed_raml', {}).get('resources', []))}")
                                for j, resource in enumerate(project.get('parsed_raml', {}).get('resources', [])[:3]):  # Show first 3
                                    st.write(f"    Resource {j+1}: {resource.get('uri', 'No URI')}")
                                    st.write(f"      Methods: {len(resource.get('methods', []))}")
                                    for k, method in enumerate(resource.get('methods', [])[:2]):  # Show first 2 methods
                                        st.write(f"        Method {k+1}: {type(method)} - {method}")
                                if len(project.get('parsed_raml', {}).get('resources', [])) > 3:
                                    st.write(f"    ... and {len(project.get('parsed_raml', {}).get('resources', [])) - 3} more resources")
            with col2:
                if st.button("⬅️ Back to Upload", use_container_width=True):
                    st.session_state.wizard_step = 1
                    st.rerun()
        else:
            st.warning("No projects found. Please go back to upload files.")
            if st.button("⬅️ Back to Upload", type="secondary", use_container_width=True):
                st.session_state.wizard_step = 1
                st.rerun()
    
    # Step 3: Download Results
    elif st.session_state.wizard_step == 3:
        st.header("📥 Step 3: Download Your Code")
        
        if st.session_state.generated_files:
            has_clients = any('client' in f for f in st.session_state.generated_files.keys())
            st.success(f"✅ Generated Flask APIs{' and Python clients' if has_clients else ''} for {len(st.session_state.projects_data)} project(s)!")
            
            # File structure overview
            st.subheader("📁 Complete Project Structure (Single ZIP Download)")
            st.info("📦 **Everything included in one ZIP file**: Flask APIs, Python clients, pytest tests, documentation")
            
            # Show structure for each project
            for project in st.session_state.projects_data:
                with st.expander(f"🔍 View Structure: {project['name']}", expanded=len(st.session_state.projects_data) == 1):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Flask application structure
                        st.write("**🐍 Flask API Server**")
                        st.write(f"`{project['name']}-flask/`")
                        flask_files = [f for f in st.session_state.generated_files.keys() if f.startswith(f"{project['name']}-flask/")]
                        if flask_files:
                            st.write(f"  ├── 📁 app/ (models, APIs, services)")
                            if generate_tests:
                                st.write(f"  ├── 📁 tests/ (pytest test suites)")
                            st.write(f"  ├── 📄 run.py (server entry point)")
                            st.write(f"  ├── 📄 requirements.txt")
                            st.write(f"  └── 📄 README.md")
                            st.write(f"  **{len([f for f in flask_files])} Flask files**")
                    
                    with col2:
                        # Client library structure (if generated)
                        if any(f.startswith(f"{project['name']}-client/") for f in st.session_state.generated_files.keys()):
                            st.write("**📚 Python Client Library**")
                            st.write(f"`{project['name']}-client/`")
                            client_files = [f for f in st.session_state.generated_files.keys() if f.startswith(f"{project['name']}-client/")]
                            st.write(f"  ├── 📁 {project['name']}_client/ (API wrapper)")
                            if generate_tests:
                                st.write(f"  ├── 📁 tests/ (client pytest tests)")
                            st.write(f"  ├── 📁 examples/ (usage examples)")
                            st.write(f"  ├── 📄 setup.py (pip installable)")
                            st.write(f"  ├── 📄 requirements.txt")
                            st.write(f"  └── 📄 README.md")
                            st.write(f"  **{len([f for f in client_files])} Client files**")
                        else:
                            st.write("**❌ Python Client**")
                            st.write("*Not generated (checkbox unchecked)*")
                
                st.write("")  # Add spacing between projects
            
            # File counts
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Files", len(st.session_state.generated_files))
            with col2:
                st.metric("Projects", len(st.session_state.projects_data))
            with col3:
                total_endpoints = sum(len(p.get('parsed_raml', {}).get('resources', [])) for p in st.session_state.projects_data)
                st.metric("Total Endpoints", total_endpoints)
            
            # Create ZIP file for download
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_path, content in st.session_state.generated_files.items():
                    zip_file.writestr(file_path, content)
            
            zip_buffer.seek(0)
            
            # Download button
            has_clients = any('client' in f for f in st.session_state.generated_files.keys())
            has_tests = generate_tests
            
            # Create descriptive filename
            if len(st.session_state.projects_data) > 1:
                download_filename = f"flask_apis_{len(st.session_state.projects_data)}_projects"
            else:
                download_filename = f"{st.session_state.projects_data[0]['name']}_complete"
            
            # Add feature suffixes
            features = []
            if has_clients:
                features.append("clients")
            if has_tests:
                features.append("tests")
            
            if features:
                download_filename += f"_with_{'_'.join(features)}"
            
            download_filename += ".zip"
            
            col1, col2 = st.columns([3, 1])
            with col1:
                # Create comprehensive download label
                download_label = f"📥 Download Complete Package"
                
                components = ["Flask APIs"]
                if has_clients:
                    components.append("Python Clients")
                if has_tests:
                    components.append("Pytest Tests")
                
                download_label += f" ({', '.join(components)})"
                
                st.download_button(
                    label=download_label,
                    data=zip_buffer.getvalue(),
                    file_name=download_filename,
                    mime="application/zip",
                    type="primary",
                    use_container_width=True
                )
            with col2:
                if st.button("🔄 Start Over", use_container_width=True):
                    st.session_state.wizard_step = 1
                    st.session_state.projects_data = []
                    st.session_state.generated_files = {}
                    st.rerun()
            
            # Show code preview for single project
            if len(st.session_state.projects_data) == 1:
                st.subheader("👀 Code Preview")
                project_name = st.session_state.projects_data[0]['name']
                preview_files = [
                    (f'{project_name}/app/__init__.py', 'python'),
                    (f'{project_name}/app/config.py', 'python'),
                    (f'{project_name}/wsgi.py', 'python'),
                    (f'{project_name}/requirements.txt', 'text')
                ]
                
                tabs = st.tabs([file.split('/')[-1] for file, _ in preview_files])
                
                for i, (file_path, language) in enumerate(preview_files):
                    with tabs[i]:
                        if file_path in st.session_state.generated_files:
                            st.code(st.session_state.generated_files[file_path], language=language)
                        else:
                            st.info("File not generated")
        else:
            st.error("No generated files found. Please go back and generate the applications.")
            if st.button("⬅️ Back to Generation", type="secondary", use_container_width=True):
                st.session_state.wizard_step = 2
                st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>Built with ❤️ using Streamlit | <strong>API Forge</strong> - Transform RAML into Production APIs</p>
        <p>© 2025 API Forge. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
