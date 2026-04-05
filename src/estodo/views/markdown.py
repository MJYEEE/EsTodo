"""Markdown rendering for EsTodo"""

import mistune
from typing import Optional


class MarkdownRenderer:
    """Markdown to HTML renderer"""

    def __init__(self):
        self._markdown = mistune.create_markdown(
            escape=True,
            plugins=['strikethrough', 'table', 'url']
        )

    def to_html(self, markdown_text: str) -> str:
        """Convert Markdown text to HTML (simplified for QTextEdit)"""
        if not markdown_text:
            return ""
        return self._markdown(markdown_text)


# Singleton instance
_renderer: Optional[MarkdownRenderer] = None


def get_markdown_renderer() -> MarkdownRenderer:
    """Get the markdown renderer singleton"""
    global _renderer
    if _renderer is None:
        _renderer = MarkdownRenderer()
    return _renderer


def render_markdown(text: str) -> str:
    """Render markdown text to HTML"""
    return get_markdown_renderer().to_html(text)
