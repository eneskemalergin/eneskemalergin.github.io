"""Tag slugs shared by the tag-frequency tools.

Templates match tags to tag pages by slug, the way Zola builds tag URLs, so
the tools count tags by the same slug.
"""

import re
import unicodedata


def slugify(text: str) -> str:
    """Approximate Zola's default slug: ASCII, lowercase, runs of other characters become '-'."""
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
