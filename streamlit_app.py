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
import toml

# Import the render_newsletter module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from render_newsletter import (
    validate_newsletter_data,
    setup_jinja_environment,
    render_newsletter,
    generate_output_filename
)

# Get version from pyproject.toml
def get_version():
    try:
        with open('pyproject.toml', 'r') as f:
            data = toml.load(f)
            return data.get('tool', {}).get('poetry', {}).get('version', 'unknown')
    except:
        return 'unknown'

APP_VERSION = get_version()

st.set_page_config(
    page_title="Newsletter Renderer",
    page_icon="📰",
    layout="wide"
)

st.title("📰 Newsletter Renderer")
st.markdown("Generate HTML newsletters from YAML data using Jinja2 templates")
st.caption(f"Version {APP_VERSION}")

# Add a tab container for the main interface
main_tabs = st.tabs(["🔧 Render Newsletter", "📋 View Prompt"])

with main_tabs[0]:

    # YAML Input Section
    st.subheader("📥 Provide YAML Content")
    input_method = st.radio(
        "Choose input method:",
        ("Upload File", "Paste Text"),
        help="Select how you want to provide the YAML data for rendering."
    )

    yaml_content = None

    if input_method == "Upload File":
        uploaded_file = st.file_uploader("Choose a YAML file", type=['yaml', 'yml'])
        
        if uploaded_file is not None:
            yaml_content = uploaded_file.read().decode('utf-8')
            st.success(f"Loaded file: {uploaded_file.name}")

    else:  # Paste Text
        yaml_text = st.text_area(
            "Paste your YAML content here:",
            height=300,
            placeholder="""newsletter:
  date: 2024-01-10
  subject: Weekly Tech Newsletter
  items:
    - company: Example Corp
      title: New Product Launch
      summary: Company announces revolutionary product...
      why_it_matters: This could change the industry...
      next_steps: Watch for the official release...""",
            help="Enter valid YAML following the expected format. Validation will occur automatically."
        )
        
        if yaml_text.strip():
            yaml_content = yaml_text

    # Add real-time validation after the input methods
    validation_message = None
    is_valid = False
    if yaml_content:
        try:
            data = yaml.safe_load(yaml_content)
            validate_newsletter_data(data)
            validation_message = st.success("✅ YAML is valid and well-structured!")
            is_valid = True
        except yaml.YAMLError as e:
            validation_message = st.error(f"❌ YAML parsing error: {e}")
        except ValueError as e:
            validation_message = st.error(f"❌ Validation error: {e}")
        except Exception as e:
            validation_message = st.error(f"❌ Unexpected error: {e}")

    # Add clear button
    if st.button("🗑️ Clear Input"):
        st.session_state.yaml_content = None  # Clear stored content
        st.experimental_rerun()  # Rerun to refresh UI

    # Remove auto-render checkbox and logic

    # But to make it work, we need to extract the render logic into a function
    # First, add this function before the tabs
    def render_newsletter_content(data):
        try:
            # Set up template directory
            template_dir = 'templates'
            template_name = 'newsletter.html.j2'
            
            # Check if template exists
            if not os.path.exists(os.path.join(template_dir, template_name)):
                st.error(f"Template not found: {os.path.join(template_dir, template_name)}")
                return None
            
            # Render the newsletter
            html_content = render_newsletter(data, template_name, template_dir)
            
            return html_content
        except Exception as e:
            st.error(f"❌ Render error: {e}")
            return None

    # Now, modify the render button and add auto-render trigger
    render_triggered = False
    if st.button("🚀 Render Newsletter", type="primary", disabled=not (yaml_content and is_valid), help="Click to generate the HTML newsletter from the provided YAML."):
        data = yaml.safe_load(yaml_content)
        html_content = render_newsletter_content(data)
        if html_content:
            st.success("✅ Newsletter rendered successfully!")

            # Optimized tabs: Make Preview default, integrate summary in expander
            tab_preview, tab_html, tab_summary = st.tabs(["👁️ Preview", "📄 HTML Code", "📊 Summary"])  # Preview first

            with tab_preview:
                # Integrate summary as expander in Preview
                with st.expander("📊 Quick Summary", expanded=True):
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

                # List items in another expander
                with st.expander("Newsletter Items:", expanded=False):
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

                # Display HTML preview
                st.components.v1.html(html_content, height=800, scrolling=True)

                # Add download button here for centralization
                st.download_button(
                    label="📥 Download HTML",
                    data=html_content,
                    file_name=generate_output_filename(date),
                    mime="text/html",
                    help="Download the rendered HTML file for use in email campaigns or archiving."
                )

            with tab_html:
                st.code(html_content, language='html')

            with tab_summary:
                # Full summary tab for those who want it separate
                st.subheader("Newsletter Items:")
                for i, item in enumerate(items, 1):
                    with st.expander(f"{i}. {item.get('title', 'Untitled')}", expanded=False):
                        if 'company' in item:
                            st.write(f"**Company:** {item['company']}")
                        st.write(f"**Summary:** {item.get('summary', 'No summary')}")
                        st.write(f"**Why it matters:** {item.get('why_it_matters', 'Not specified')}")
                        if 'next_steps' in item:
                            st.write(f"**Next steps:** {item['next_steps']}")

        # Remove the old try-except since it's now in the function

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