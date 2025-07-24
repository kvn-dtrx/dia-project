# ---
# description:
# ---

# ---

from pathlib import Path
from jinja2 import Template
from typing import List


def build_file_with_header_from_template(
    template_path: Path,
    file_type: str,
    filename: str,
    content_files: List[Path],
    output_path: Path,
) -> None:
    with template_path.open("r", encoding="utf-8") as f:
        template_text = f.read()
    template = Template(template_text)
    header_text = template.render(type=file_type, filename=filename)

    combined_contents: List[str] = []
    for file_path in content_files:
        with file_path.open("r", encoding="utf-8") as f:
            combined_contents.append(f.read())

    final_text = header_text + "\n\n" + "\n\n".join(combined_contents)

    with output_path.open("w", encoding="utf-8") as f:
        f.write(final_text)
