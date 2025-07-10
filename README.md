# SimpleKYC Email Newsletter Generator

A Python-based HTML newsletter generator designed for creating professional email newsletters focused on AI, KYC (Know Your Customer), and AML (Anti-Money Laundering) compliance topics. This tool streamlines the process of transforming structured data into beautifully formatted, email-optimized HTML newsletters.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Data Structure](#data-structure)
- [Customization](#customization)
- [Template System](#template-system)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Overview

The SimpleKYC Email Newsletter Generator is a command-line tool that:
- Reads newsletter content from YAML files
- Processes data through customizable Jinja2 templates
- Generates responsive HTML emails optimized for various email clients
- Automatically formats and cleans content for professional presentation

This tool is particularly useful for companies in the RegTech, compliance, and financial services sectors who need to regularly communicate industry updates, competitor analysis, and strategic insights to their teams.

## Features

### Core Features
- **YAML-based Content Management**: Structure your newsletter content in easy-to-edit YAML files
- **Professional HTML Templates**: Email-optimized, responsive design that works across all major email clients
- **Automatic Formatting**: Built-in filters for bullet points, citation cleaning, and text formatting
- **Team-based Organization**: Tag content by department (Product, Engineering, Operations, etc.)
- **Rich Content Sections**: Support for summaries, "why it matters" analysis, and actionable next steps
- **Batch Processing**: Generate multiple newsletters from different YAML files

### Technical Features
- **Jinja2 Template Engine**: Flexible and powerful templating system
- **CSS Inlining**: Automatic CSS inlining for maximum email client compatibility
- **Command-line Interface**: Easy integration with CI/CD pipelines
- **Extensible Architecture**: Easy to add new content types and formatting options

## Requirements

- Python 3.8 or higher
- Poetry (for dependency management)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/simplekyc-email.git
   cd simplekyc-email/email
   ```

2. **Install dependencies using Poetry**:
   ```bash
   poetry install
   ```

3. **Activate the virtual environment**:
   ```bash
   poetry shell
   ```

## Usage

### Basic Usage

Generate a newsletter from a YAML file:

```bash
python render_newsletter.py test.yaml
```

This will create an HTML file in the `output/` directory with the naming convention `newsletter_YYYYMMDD.html`.

### Command-line Options

```bash
python render_newsletter.py [OPTIONS] YAML_FILE

Options:
  --yaml PATH           Path to YAML data file (default: test.yaml)
  --template PATH       Template filename (default: newsletter.html.j2)
  --template-dir PATH   Template directory (default: templates)
  --output PATH         Output HTML file path (default: auto-generated from date)
  --output-dir PATH     Output directory (default: output)
  --preview            Open the generated newsletter in browser
  --verbose            Enable verbose logging for debugging
  -h, --help           Show help message
```

### Examples

1. **Generate newsletter with custom output directory**:
   ```bash
   python render_newsletter.py --yaml data/march_2025.yaml --output-dir newsletters/2025/march/
   ```

2. **Use a custom template**:
   ```bash
   python render_newsletter.py --yaml test.yaml --template custom_newsletter.html.j2
   ```

3. **Generate and preview in browser**:
   ```bash
   python render_newsletter.py --yaml test.yaml --preview
   ```

4. **Debug mode with verbose logging**:
   ```bash
   python render_newsletter.py --yaml test.yaml --verbose
   ```

5. **Custom output file path**:
   ```bash
   python render_newsletter.py --yaml test.yaml --output /var/www/newsletters/latest.html
   ```

## Data Structure

Newsletter content is defined in YAML format. Here's the structure:

```yaml
newsletter:
  date: "YYYY-MM-DD"  # Newsletter date (used for filename)
  items:
    - company: "Company Name"
      title: "Newsletter Item Title"
      summary: "Brief summary of the news item"
      why_it_matters: |
        Explanation of why this news is significant.
        Can include multiple paragraphs.
        - Bullet points are automatically formatted
        - **Bold text** is supported
      next_steps: |
        Actionable items or strategic considerations.
        - Can also include bullet points
        - Multiple paragraphs supported
      teams:
        - Product
        - Engineering
        - Operations
      link: "https://source-url.com"  # Optional
      source: "Publication Name"      # Optional
```

### Field Descriptions

- **date** (required): Newsletter date in YYYY-MM-DD format
- **items** (required): Array of newsletter items
  - **company** (required): Company or organization name
  - **title** (required): Headline or title of the news item
  - **summary** (required): Brief overview of the news
  - **why_it_matters** (required): Analysis of the significance
  - **next_steps** (required): Recommended actions or considerations
  - **teams** (optional): List of relevant teams/departments
  - **link** (optional): URL to the source article
  - **source** (optional): Name of the publication or source

### Formatting Options

The following text formatting is supported in summary, why_it_matters, and next_steps fields:

- **Bullet Points**: Lines starting with `-` are converted to HTML bullets
- **Bold Text**: Text wrapped in `**` becomes bold
- **Paragraphs**: Blank lines create paragraph breaks
- **Citation Cleaning**: AI-generated citations like `[1]`, `[2]` are automatically removed

## Customization

### Template Customization

The newsletter template (`templates/newsletter.html.j2`) can be customized to match your brand:

1. **Colors**: Update the color scheme in the CSS section
2. **Logo**: Add your company logo to the header
3. **Footer**: Customize the footer with your contact information
4. **Sections**: Add or remove content sections as needed

### Adding Custom Filters

To add custom Jinja2 filters for text processing:

```python
# In render_newsletter.py
def my_custom_filter(text):
    # Your custom processing logic
    return processed_text

# Register the filter
env.filters['my_filter'] = my_custom_filter
```

### Extending Content Types

To add new content types or fields:

1. Update your YAML structure with new fields
2. Modify the template to display the new fields
3. Add any necessary processing filters

## Template System

The template system uses Jinja2 and includes:

### Built-in Filters

- **`format_bullets`**: Converts markdown-style bullets to HTML list items
- **`clean_citations`**: Removes AI-generated citation markers
- **`nl2br`**: Converts newlines to HTML line breaks

### Template Structure

```html
<!-- Main container with responsive design -->
<table class="container">
  <!-- Header section -->
  <tr class="header">
    <!-- Company branding -->
  </tr>
  
  <!-- Content items loop -->
  {% for item in newsletter.items %}
    <tr class="content-item">
      <!-- Item header with company and title -->
      <!-- Summary section (green border) -->
      <!-- Why it matters section (yellow background) -->
      <!-- Next steps section (blue background) -->
      <!-- Teams and metadata -->
    </tr>
  {% endfor %}
  
  <!-- Footer section -->
</table>
```

### CSS Styling

The template includes:
- **Responsive Design**: Adapts to mobile and desktop email clients
- **Inline CSS**: Ensures compatibility with all email clients
- **Color-coded Sections**: Visual hierarchy for different content types
- **Clean Typography**: Professional, readable fonts

## Development

### Project Structure

```
email/
├── README.md                    # This file
├── pyproject.toml              # Poetry configuration
├── render_newsletter.py        # Main script
├── test.yaml                   # Sample data
├── templates/                  # Template directory
│   └── newsletter.html.j2      # Main email template
└── output/                     # Generated newsletters
```

### Running Tests

```bash
poetry run pytest
```

### Code Formatting

```bash
poetry run black render_newsletter.py
poetry run flake8 render_newsletter.py
```

### Adding Dependencies

```bash
poetry add package-name
poetry add --dev package-name  # For development dependencies
```

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Contribution Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation as needed
- Keep commits atomic and descriptive

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions, issues, or feature requests, please:
- Open an issue on GitHub
- Contact the SimpleKYC development team
- Check the documentation for common solutions

---

Built with ❤️ by the SimpleKYC team for the RegTech community.