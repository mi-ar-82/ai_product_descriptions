# File: app/services/text_utils.py
import markdown
import re
from bs4 import BeautifulSoup


def convert_markdown_to_html(markdown_text: str) -> str:
    """
    Convert markdown formatted text to HTML.
    """
    print(f"Debug: Converting markdown to HTML, type: {type(markdown_text)}")
    html = markdown.markdown(markdown_text)
    print(f"Debug: Converted HTML type: {type(html)}")
    return html


def convert_markdown_to_plain_text(markdown_text: str) -> str:
    """
    Remove markdown formatting to get plain text.
    """
    print(f"Debug: Converting markdown to plain text, type: {type(markdown_text)}")
    # Remove headers
    text = re.sub(r'#+\s+(.*)', r'\1', markdown_text)
    # Remove bold/italic
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    # Remove links
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    # Remove code blocks
    text = re.sub(r'``````', '', text, flags = re.DOTALL)
    # Remove inline code
    text = re.sub(r'`(.*?)`', r'\1', text)
    # Remove bullet points
    text = re.sub(r'^\s*[\*\-\+]\s+(.*?)$', r'\1', text, flags = re.MULTILINE)
    # Remove numbered lists
    text = re.sub(r'^\s*\d+\.\s+(.*?)$', r'\1', text, flags = re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'---+', '', text)
    # Clean up multiple line breaks
    text = re.sub(r'\n\s*\n', '\n\n', text)
    print(f"Debug: Converted plain text type: {type(text.strip())}")
    return text.strip()


def convert_html_to_markdown(html_text: str) -> str:
    """
    Convert HTML content to markdown format.

    Args:
        html_text (str): HTML-formatted text to convert

    Returns:
        str: Markdown-formatted text
    """
    print(f"Debug: Converting HTML to markdown, type: {type(html_text)}")

    try:
        # Import here to avoid dependency issues if the package is missing
        import html2text

        # Create an instance of the HTML2Text parser
        parser = html2text.HTML2Text()

        # Configure the parser
        parser.ignore_links = False
        parser.ignore_images = False
        parser.body_width = 0  # No wrapping
        parser.unicode_snob = True  # Use Unicode instead of ASCII

        # Convert HTML to markdown
        markdown_text = parser.handle(html_text)

        print(f"Debug: Converted markdown type: {type(markdown_text)}")
        return markdown_text.strip()
    except ImportError:
        print("Debug: html2text package not found. Falling back to simple conversion.")
        # Simple fallback if html2text is not installed
        soup = BeautifulSoup(html_text, 'html.parser')
        return soup.get_text()



def convert_html_to_plain_text(html_text: str) -> str:
    """
    Convert HTML content to plain text by removing all HTML tags.

    Args:
        html_text (str): HTML-formatted text to convert

    Returns:
        str: Plain text with HTML tags removed
    """
    print(f"Debug: Converting HTML to plain text, type: {type(html_text)}")

    # Handle None input
    if html_text is None:
        print("Debug: HTML content is None, returning empty string")
        return ""

    try:
        # Use BeautifulSoup to parse the HTML
        soup = BeautifulSoup(html_text, 'html.parser')

        # Get text content
        plain_text = soup.get_text(separator = ' ', strip = True)

        # Clean up excessive whitespace
        plain_text = re.sub(r'\s+', ' ', plain_text).strip()

        print(f"Debug: Converted plain text type: {type(plain_text)}")
        return plain_text
    except Exception as e:
        print(f"Debug: Error converting HTML to plain text: {e}")
        # Simple fallback using regex if BeautifulSoup fails
        if html_text:  # Make sure html_text is not None or empty
            text = re.sub(r'<[^>]+>', ' ', html_text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        return ""
