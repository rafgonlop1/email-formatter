#!/usr/bin/env python3
"""
Streamlit Newsletter Renderer
A web interface for rendering newsletters from YAML data
"""

import streamlit as st
import yaml
import tempfile
import os
from pathlib import Path
import subprocess
import sys

# Import the render_newsletter module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from render_newsletter import (
    validate_newsletter_data,
    setup_jinja_environment,
    render_newsletter,
    generate_output_filename
)

st.set_page_config(
    page_title="Newsletter Renderer",
    page_icon="📰",
    layout="wide"
)

st.title("📰 Newsletter Renderer")
st.markdown("Generate HTML newsletters from YAML data using Jinja2 templates")

# Add a tab container for the main interface
main_tabs = st.tabs(["🔧 Render Newsletter", "📋 View Prompt"])

with main_tabs[0]:

    # Create two columns for input methods
    col1, col2 = st.columns(2)

    yaml_content = None

    with col1:
        st.subheader("📁 Upload YAML File")
        uploaded_file = st.file_uploader("Choose a YAML file", type=['yaml', 'yml'])
        
        if uploaded_file is not None:
            yaml_content = uploaded_file.read().decode('utf-8')
            st.success(f"Loaded file: {uploaded_file.name}")

    with col2:
        st.subheader("📝 Paste YAML Content")
        yaml_text = st.text_area(
            "Or paste your YAML content here:",
            height=400,
            placeholder="""newsletter:
  date: 2024-01-10
  subject: Weekly Tech Newsletter
  items:
    - company: Example Corp
      title: New Product Launch
      summary: Company announces revolutionary product...
      why_it_matters: This could change the industry...
      next_steps: Watch for the official release..."""
        )
        
        if yaml_text.strip():
            yaml_content = yaml_text

    # Display current YAML content
    if yaml_content:
        st.divider()
        with st.expander("📄 Current YAML Content", expanded=False):
            st.code(yaml_content, language='yaml')

    # Render button
    if st.button("🚀 Render Newsletter", type="primary", disabled=not yaml_content):
        try:
            # Parse YAML
            data = yaml.safe_load(yaml_content)
        
            # Validate data
            validate_newsletter_data(data)
            
            # Set up template directory
            template_dir = 'templates'
            template_name = 'newsletter.html.j2'
            
            # Check if template exists
            if not os.path.exists(os.path.join(template_dir, template_name)):
                st.error(f"Template not found: {os.path.join(template_dir, template_name)}")
                st.stop()
            
            # Render the newsletter
            html_content = render_newsletter(data, template_name, template_dir)
            
            # Display success message
            st.success("✅ Newsletter rendered successfully!")
            
            # Create tabs for different views
            tab1, tab2, tab3 = st.tabs(["📊 Summary", "👁️ Preview", "📄 HTML Code"])
        
            with tab1:
                # Extract summary information
                if 'newsletter' in data:
                    newsletter = data['newsletter']
                    date = newsletter.get('date', 'Unknown')
                    subject = newsletter.get('subject', 'No subject')
                    items_count = len(newsletter.get('items', []))
                else:
                    date = data.get('newsletter_date', 'Unknown')
                    subject = data.get('subject', 'No subject')
                    items_count = len(data.get('items', []))
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Date", date)
                with col2:
                    st.metric("Items", items_count)
                with col3:
                    st.metric("Subject", subject)
                
                # List items
                st.subheader("Newsletter Items:")
                if 'newsletter' in data:
                    items = data['newsletter'].get('items', [])
                else:
                    items = data.get('items', [])
                    
                for i, item in enumerate(items, 1):
                    with st.expander(f"{i}. {item.get('title', 'Untitled')}", expanded=False):
                        if 'company' in item:
                            st.write(f"**Company:** {item['company']}")
                        st.write(f"**Summary:** {item.get('summary', 'No summary')}")
                        st.write(f"**Why it matters:** {item.get('why_it_matters', 'Not specified')}")
                        if 'next_steps' in item:
                            st.write(f"**Next steps:** {item['next_steps']}")
            
            with tab2:
                # Display HTML preview in an iframe
                st.components.v1.html(html_content, height=800, scrolling=True)
            
            with tab3:
                # Display raw HTML code
                st.code(html_content, language='html')
                
                # Download button
                st.download_button(
                    label="📥 Download HTML",
                    data=html_content,
                    file_name=generate_output_filename(date),
                    mime="text/html"
                )
                
        except yaml.YAMLError as e:
            st.error(f"❌ YAML parsing error: {e}")
        except ValueError as e:
            st.error(f"❌ Validation error: {e}")
            st.info("Please check your YAML structure matches the expected format")
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")

with main_tabs[1]:
    st.subheader("📋 AI Research Prompt")
    st.markdown("This is the prompt used in ChatGPT Deep Research to generate newsletter YAMLs")
    
    # Check if prompt.md exists
    prompt_file_path = 'prompt.md'
    if os.path.exists(prompt_file_path):
        with open(prompt_file_path, 'r', encoding='utf-8') as f:
            prompt_content = f.read()
        
        # Add some context
        st.info("💡 Use this prompt with ChatGPT's Deep Research feature to automatically generate newsletter content based on the latest AI news relevant to Simple KYC.")
        
        # Display the prompt in a nice format
        with st.expander("View Full Prompt", expanded=True):
            st.code(prompt_content, language="markdown")
        
        
        # Add usage instructions
        with st.expander("📖 How to Use This Prompt"):
            st.markdown("""
            1. **Open ChatGPT** and enable the Deep Research feature
            2. **Copy this entire prompt** and paste it into ChatGPT
            3. **Wait for the research** to complete (usually 3-5 minutes)
            4. **Copy the generated YAML** from ChatGPT's response
            5. **Paste it here** in the Newsletter Renderer tab
            6. **Click Render** to generate your HTML newsletter
            
            **Tips:**
            - The prompt is optimized for finding AI news relevant to KYC/AML compliance
            - It focuses on competitors like Fenergo, ComplyAdvantage, Quantexa, etc.
            - Each newsletter item includes actionable insights and next steps
            - If no relevant news is found, it generates a practical AI tutorial instead
            """)
    else:
        st.error(f"❌ Prompt file not found: {prompt_file_path}")
        st.info("Make sure prompt.md exists in the same directory as this app.")

# Instructions
with st.sidebar:
    st.header("📖 Instructions")
    st.markdown("""
    1. **Upload a YAML file** or **paste YAML content** in the text area
    2. Click **Render Newsletter** to generate the HTML
    3. View the summary, preview, or HTML code in the tabs
    4. Download the generated HTML file if needed
    
    ### Expected YAML Format:
    ```yaml
    newsletter:
      date: YYYY-MM-DD
      subject: Newsletter Subject
      items:
        - company: Company Name
          title: Item Title
          summary: Brief summary
          why_it_matters: Importance
          next_steps: What to do next
    ```
    
    Or legacy format:
    ```yaml
    newsletter_date: YYYY-MM-DD
    subject: Newsletter Subject
    items:
      - title: Item Title
        summary: Brief summary
        why_it_matters: Importance
    ```
    """)
    
    st.divider()
    st.caption("Built with Streamlit and Jinja2")