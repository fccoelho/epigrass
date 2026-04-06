"""Template rendering with Jinja2

This module provides safe template rendering using Jinja2,
replacing the insecure exec()-based approach in the old report.py.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
import logging

logger = logging.getLogger(__name__)


class TemplateRenderer:
    """Jinja2-based template renderer for report generation

    Provides safe, maintainable template rendering without code execution.
    """

    def __init__(self, template_dir: Optional[Path] = None):
        """Initialize template renderer

        Args:
            template_dir: Directory containing Jinja2 templates.
                         If None, uses default templates directory.
        """
        if template_dir is None:
            template_dir = Path(__file__).parent / "templates"

        self.template_dir = Path(template_dir)

        if not self.template_dir.exists():
            logger.warning(f"Template directory does not exist: {self.template_dir}")

        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        self.env.filters["latex"] = self._latex_filter
        self.env.filters["format_number"] = self._format_number_filter
        self.env.filters["format_scientific"] = self._format_scientific_filter

        logger.debug(f"TemplateRenderer initialized with dir: {self.template_dir}")

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a template with context

        Args:
            template_name: Name of template file (e.g., 'network.md.j2')
            context: Dictionary of variables to pass to template

        Returns:
            Rendered template as string

        Raises:
            TemplateNotFound: If template file doesn't exist
            TemplateSyntaxError: If template has syntax errors
        """
        logger.debug(f"Rendering template: {template_name}")

        template = self.env.get_template(template_name)
        rendered = template.render(**context)

        logger.debug(f"Template rendered successfully: {len(rendered)} chars")
        return rendered

    def render_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """Render a template from string

        Args:
            template_string: Template content as string
            context: Dictionary of variables to pass to template

        Returns:
            Rendered template as string
        """
        template = self.env.from_string(template_string)
        return template.render(**context)

    @staticmethod
    def _latex_filter(text: Any) -> str:
        """Escape LaTeX special characters

        Args:
            text: Text to escape

        Returns:
            LaTeX-escaped text
        """
        if not isinstance(text, str):
            text = str(text)

        # LaTeX special characters that need escaping
        replacements = {
            "\\": r"\textbackslash{}",
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "~": r"\textasciitilde{}",
            "^": r"\textasciicircum{}",
        }

        for char, replacement in replacements.items():
            text = text.replace(char, replacement)

        return text

    @staticmethod
    def _format_number_filter(value: Any, decimals: int = 2) -> str:
        """Format number with thousand separators

        Args:
            value: Number to format
            decimals: Number of decimal places

        Returns:
            Formatted number string
        """
        try:
            return f"{float(value):,.{decimals}f}"
        except (ValueError, TypeError):
            return str(value)

    @staticmethod
    def _format_scientific_filter(value: Any, decimals: int = 2) -> str:
        """Format number in scientific notation

        Args:
            value: Number to format
            decimals: Number of decimal places

        Returns:
            Formatted number string in scientific notation
        """
        try:
            return f"{float(value):.{decimals}e}"
        except (ValueError, TypeError):
            return str(value)
