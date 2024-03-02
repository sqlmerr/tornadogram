from typing import Tuple, Union


def split_command(text: str, prefix: str) -> Union[Tuple[str, str, str], Tuple[str, str, str, str]]:
    if (
        text
        and len(text) > len(prefix)
        and text.startswith(prefix)
        and text.split()[0].count(prefix) == 1
    ):
        command, *args = text[len(prefix) :].split(maxsplit=1)
    elif (
        text
        and len(text) > len(prefix)
        and text.startswith(prefix)
        and text.split()[0].count(prefix) == 2
    ):
        router = text.split()[0].split(".")[1]
        other = text.removeprefix(f".{router}")
        command, *args = other[len(prefix) :].split(maxsplit=1)
        return prefix, router, command, args[-1] if args else ""
    else:
        return "", "", ""

    return prefix, command, args[-1] if args else ""
