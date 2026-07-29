import os


def sanitize_filename(filename: str) -> str:
    FORBIDDEN_CHARS = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\n', '\r', '\t']

    clean_name = filename
    for char in FORBIDDEN_CHARS:
        clean_name = clean_name.replace(char, '')

    clean_name = clean_name.replace(' ', '_').strip('_')

    if not clean_name:
        clean_name = "article"

    return clean_name


def save_article(title: str, content: str, output_format: str = "md", custom_filename: str = None) -> str:
    if custom_filename:
        base_name = custom_filename
    else:
        base_name = sanitize_filename(title)

    fmt = output_format.lower()
    if fmt not in ["md", "txt"]:
        fmt = "md"

    if not base_name.endswith(f".{fmt}"):
        full_filename = f"{base_name}.{fmt}"
    else:
        full_filename = base_name

    if fmt == "md":
        formatted_text = f"# {title}\n\n{content}\n"
    else:
        underline = "=" * len(title)
        formatted_text = f"{title}\n{underline}\n\n{content}\n"

    with open(full_filename, "w", encoding="utf-8") as f:
        f.write(formatted_text)

    return full_filename