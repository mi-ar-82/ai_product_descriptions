# File: app/services/text_utils.py
import markdown
import re

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
    text = re.sub(r'``````', '', text, flags=re.DOTALL)
    # Remove inline code
    text = re.sub(r'`(.*?)`', r'\1', text)
    # Remove bullet points
    text = re.sub(r'^\s*[\*\-\+]\s+(.*?)$', r'\1', text, flags=re.MULTILINE)
    # Remove numbered lists
    text = re.sub(r'^\s*\d+\.\s+(.*?)$', r'\1', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'---+', '', text)
    # Clean up multiple line breaks
    text = re.sub(r'\n\s*\n', '\n\n', text)
    print(f"Debug: Converted plain text type: {type(text.strip())}")
    return text.strip()
