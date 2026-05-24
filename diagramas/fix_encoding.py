#!/usr/bin/env python3
"""Corrige mojibake (Latin-1 via UTF-8) nos arquivos drawio originais."""
import sys

def fix(text):
    return text.encode('latin-1').decode('utf-8')

for path in sys.argv[1:]:
    content = open(path, encoding='latin-1').read()
    open(path, 'w', encoding='utf-8').write(fix(content))
    print(f"Fixed: {path}")
