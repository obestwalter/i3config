#!/home/ob/.virtualenvs/syshelpers/bin/python
import subprocess

import clipboard


def replace_clipboard():
    text = clipboard.paste()
    new_text = []
    for line in text.splitlines():
        line = line.strip().replace(">>> ", "").replace("... ", "")
        if not line.startswith("..."):
            new_text.append(line)
    output = "\n".join(new_text)
    subprocess.call(["notify-send", f"replace clipboard: {output}"])
    clipboard.copy(output)


def test():
    clipboard.copy("""
    >>> def count_down(value):
    ...     for x in range(value, 0, -1):
    ...     yield x
    ...   

    """)
    print(replace_clipboard())


if __name__ == '__main__':
    print(replace_clipboard(), end="")
