"""Compile inline JavaScript from the existing single-page web UI with Node."""
import os
import re
import subprocess
import tempfile


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html_path = os.path.join(root, "web_app", "index.html")
    with open(html_path, "r", encoding="utf-8") as handle:
        html = handle.read()
    scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script\s*>", html, flags=re.IGNORECASE | re.DOTALL)
    if not scripts:
        raise SystemExit("No inline script blocks found in web_app/index.html")
    node = "node"
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        script_path = handle.name
        handle.write("\n;\n".join(scripts))
    try:
        completed = subprocess.run([node, "--check", script_path], check=False, text=True, capture_output=True)
        if completed.returncode:
            raise SystemExit(completed.stderr or completed.stdout or "Node syntax check failed")
        print(f"JavaScript syntax check passed ({len(scripts)} inline script block(s)).")
    finally:
        os.unlink(script_path)


if __name__ == "__main__":
    main()
