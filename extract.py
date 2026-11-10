import os
import re

modules = ['school', 'school_fees']
strings = set()

xml1 = re.compile(r'string="([^"]+)"')
xml2 = re.compile(r'help="([^"]+)"')
py1 = re.compile(r'_\("([^"]+)"\)')
py2 = re.compile(r"_\('([^']+)'\)")
label_re = re.compile(r'<label\s+[^>]*\bstring="([^"]+)"') # already covered by string="" mostly

for mod in modules:
    for root, dirs, files in os.walk(mod):
        for f in files:
            p = os.path.join(root, f)
            try:
                content = open(p, 'r', encoding='utf-8').read()
                if f.endswith('.xml'):
                    strings.update(xml1.findall(content))
                    strings.update(xml2.findall(content))
                elif f.endswith('.py'):
                    strings.update(py1.findall(content))
                    strings.update(py2.findall(content))
            except Exception as e:
                print(f"Error reading {p}: {e}")

with open('strings.txt', 'w', encoding='utf-8') as out:
    for s in sorted(strings):
        out.write(s + '\n')
print(f"Extracted {len(strings)} strings.")
