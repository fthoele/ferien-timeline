#!/usr/bin/env python3
"""Assemble index.html from template.html with data embedded inline."""
from pathlib import Path

template = Path("template.html").read_text()
# Escape "</" so the JSON can never terminate the <script> block early.
data = Path("data.json").read_text().strip().replace("</", "<\\/")

html = template.replace("__DATA__", data)
Path("index.html").write_text(html)
print(f"wrote index.html ({len(html)} bytes)")
