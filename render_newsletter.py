#!/usr/bin/env python3
"""
Newsletter Renderer
Generates HTML newsletters from YAML data using Jinja2 templates.
"""

import argparse
import yaml
import os
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
import re
import webbrowser
import tempfile
import logging


def validate_newsletter_data(data: dict) -> None:
    """Validate required fields in newsletter data."""
    if not data:
        raise ValueError("YAML file is empty")
    
    # Support both formats: with and without 'newsletter' root key
    if 'newsletter' in data:
        newsletter = data['newsletter']
        date_field = 'date'
    else:
        # Legacy format - data is directly at root level
        newsletter = data
        date_field = 'newsletter_date'
    
    # Check required fields
    required_fields = [date_field, 'items']
    for field in required_fields:
        if field not in newsletter:
            raise ValueError(f"Missing required field '{field}'")
    
    # Validate items
    if not newsletter['items']:
        raise ValueError("Newsletter must have at least one item")
    
    for i, item in enumerate(newsletter['items']):
        # Different required fields based on format
        if 'newsletter' in data:
            required_item_fields = ['company', 'title', 'summary', 'why_it_matters', 'next_steps']
        else:
            # Legacy format uses different field names
            required_item_fields = ['title', 'summary', 'why_it_matters']
        
        for field in required_item_fields:
            if field not in item:
                raise ValueError(f"Missing required field '{field}' in item {i+1}")


def load_yaml_data(yaml_path: str) -> dict:
    """Load and parse YAML newsletter data."""
    try:
        with open(yaml_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        
        # Validate the data
        validate_newsletter_data(data)
        
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"YAML file not found: {yaml_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file: {e}")


def setup_jinja_environment(template_dir: str) -> Environment:
    """Set up Jinja2 environment with template directory."""

    def format_bullet(text: str) -> str:
        """Convert a raw bullet line (possibly markdown-style) to clean HTML.

        Steps:
        1. Remove leading bullet characters (e.g. •, -, *).
        2. Replace **bold** markdown with <strong>bold</strong>.
        3. Strip out any leftover citation tokens produced by the AI assistant.
        """

        if not text:
            return ""

        # Trim whitespace and a single leading bullet symbol (• or -) if present.
        cleaned = re.sub(r"^\s*[\u2022\-]\s*", "", text.strip())

        # Convert markdown bold (**text**) to <strong>text</strong>
        cleaned = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", cleaned)

        # Remove stray citation tokens like ':contentReference[oaicite:'
        cleaned = cleaned.replace(':contentReference[oaicite:', '').replace(']{index=', '').replace('}', '')

        return cleaned

    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(['html', 'xml'])
    )

    def clean_citations(text: str) -> str:
        """Remove AI-generated citation markers like [1], [2], etc."""
        if not text:
            return ""
        # Remove numbered citations in brackets
        cleaned = re.sub(r'\[\d+\]', '', text)
        # Remove any other AI citation patterns
        cleaned = re.sub(r':contentReference\[oaicite:[^\]]+\]\{index=\d+\}', '', cleaned)
        return cleaned
    
    def nl2br(text: str) -> str:
        """Convert newlines to HTML line breaks."""
        if not text:
            return ""
        return text.replace('\n', '<br>')
    
    def format_bullets(text: str) -> str:
        """Convert lines starting with - into HTML list items."""
        if not text:
            return ""
        
        lines = text.strip().split('\n')
        result = []
        in_list = False
        
        for line in lines:
            # Check if line starts with a bullet (- or •)
            if line.strip().startswith(('-', '•')):
                if not in_list:
                    result.append('<ul style="margin: 0; padding-left: 18px; font-size: 14px; color: #856404; list-style-type: disc;">')
                    in_list = True
                # Use the existing format_bullet function
                bullet_text = format_bullet(line)
                result.append(f'<li style="margin-bottom: 5px;">{bullet_text}</li>')
            else:
                if in_list:
                    result.append('</ul>')
                    in_list = False
                if line.strip():
                    result.append(line)
        
        # Close list if still open
        if in_list:
            result.append('</ul>')
        
        return '\n'.join(result)
    
    # Register custom filters
    env.filters['format_bullet'] = format_bullet
    env.filters['format_bullets'] = format_bullets
    env.filters['clean_citations'] = clean_citations
    env.filters['nl2br'] = nl2br

    return env


def render_newsletter(data: dict, template_name: str, template_dir: str) -> str:
    """Render newsletter HTML from data and template."""
    env = setup_jinja_environment(template_dir)
    template = env.get_template(template_name)
    
    # Add current timestamp if not present
    if 'generated_at' not in data:
        data['generated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return template.render(**data)


def ensure_output_directory(output_path: str) -> None:
    """Create output directory if it doesn't exist."""
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)


def generate_output_filename(newsletter_date: str) -> str:
    """Generate output filename based on newsletter date."""
    # Convert date to filename-friendly format
    try:
        date_obj = datetime.strptime(newsletter_date, '%Y-%m-%d')
        date_str = date_obj.strftime('%Y%m%d')
    except ValueError:
        # Fallback to current date if parsing fails
        date_str = datetime.now().strftime('%Y%m%d')
    
    return f"newsletter_{date_str}.html"


def main():
    """Main function to process command line arguments and generate newsletter."""
    parser = argparse.ArgumentParser(description='Generate HTML newsletter from YAML data')
    parser.add_argument(
        '--yaml', 
        default='test.yaml',
        help='Path to YAML data file (default: test.yaml)'
    )
    parser.add_argument(
        '--template',
        default='newsletter.html.j2',
        help='Template filename (default: newsletter.html.j2)'
    )
    parser.add_argument(
        '--template-dir',
        default='templates',
        help='Template directory (default: templates)'
    )
    parser.add_argument(
        '--output',
        help='Output HTML file path (default: auto-generated from date)'
    )
    parser.add_argument(
        '--output-dir',
        default='output',
        help='Output directory (default: output)'
    )
    parser.add_argument(
        '--preview',
        action='store_true',
        help='Open the generated newsletter in the default browser'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    logger = logging.getLogger(__name__)
    
    try:
        # Load YAML data
        logger.info(f"Loading data from {args.yaml}...")
        newsletter_data = load_yaml_data(args.yaml)
        logger.debug(f"Loaded {len(newsletter_data.get('newsletter', {}).get('items', []))} items")
        
        # Generate output filename if not specified
        if args.output:
            output_path = args.output
        else:
            # Fix: Look for date in the correct location (support both formats)
            if 'newsletter' in newsletter_data:
                newsletter_date = newsletter_data.get('newsletter', {}).get('date', '')
            else:
                newsletter_date = newsletter_data.get('newsletter_date', '')
            filename = generate_output_filename(newsletter_date)
            output_path = os.path.join(args.output_dir, filename)
        
        # Ensure output directory exists
        ensure_output_directory(output_path)
        
        # Render newsletter
        logger.info(f"Rendering newsletter using template {args.template}...")
        html_content = render_newsletter(
            newsletter_data, 
            args.template, 
            args.template_dir
        )
        logger.debug(f"Generated {len(html_content)} characters of HTML")
        
        # Write output file
        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write(html_content)
        
        logger.info(f"Newsletter generated successfully: {output_path}")
        
        # Open in browser if preview mode
        if args.preview:
            logger.info("Opening newsletter in browser...")
            # Use file:// URL for local file
            file_url = f"file:///{os.path.abspath(output_path).replace(os.sep, '/')}"
            webbrowser.open(file_url)
        
        # Print summary (support both formats)
        if 'newsletter' in newsletter_data:
            newsletter = newsletter_data.get('newsletter', {})
            item_count = len(newsletter.get('items', []))
            newsletter_date = newsletter.get('date', 'Unknown')
            subject = newsletter.get('subject', 'No subject')
        else:
            item_count = len(newsletter_data.get('items', []))
            newsletter_date = newsletter_data.get('newsletter_date', 'Unknown')
            subject = newsletter_data.get('subject', 'No subject')
        
        print(f"\nNewsletter Summary:")
        print(f"  Date: {newsletter_date}")
        print(f"  Subject: {subject}")
        print(f"  Items: {item_count}")
        print(f"  Output: {output_path}")
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 1
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        logger.info("Please check your YAML file structure")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main()) 