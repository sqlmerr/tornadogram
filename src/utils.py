from typing import Tuple


def split_command(text: str) -> Tuple[str, str, str]:
    prefix = "."

    if (
        text
        and len(text) > len(prefix)
        and text.startswith(prefix)
    ):
        command, *args = text[len(prefix):].split(maxsplit=1)
    else:
        return "", "", ""

    return prefix, command, args[-1] if args else ""
