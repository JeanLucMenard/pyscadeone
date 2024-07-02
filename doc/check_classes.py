"""
Check classes in .rst vs classes in .py, produce a report on stdout
Usage: python autoclass.py
"""

import re
from pathlib import Path
from pprint import pprint

autoclassRE = re.compile(r'^\.\. autoclass::\s*(\S+)', re.MULTILINE)
pyclassRE = re.compile(r'^class\s+(\w+)\s*[:(]', re.MULTILINE)

# Documented with .. automodule:: directive
py_skip = ('loader.py',
           'logger.py',
           'scadeoneexception.py')

class_skip = (
    'Asset',
    'FileAsset',
    'IProject',
    'IScadeOne',
    'JobAsset',
    'JSONAsset',
    'ProjectAsset',
    'StringAsset',
    'SwanCode',
)

classes = {}
for py in Path.cwd().glob('../src/**/*.py'):
    if py.parent.stem == 'mapping':
        continue
    if py.name in py_skip:
        continue
    for found in pyclassRE.findall(py.read_text()):
        if found in class_skip:
            continue
        if found in classes:
            print(f"""
Multiple Class {found}:
   - {py}
   - {classes[found]}""")
            exit(1)
        classes[found] = py

autoclasses = {}
for rst in Path.cwd().glob('**/*.rst'):
    for found in autoclassRE.findall(rst.read_text()):
        if found in autoclasses:
            print(f"""
Autoclass {found}:
   - {rst},
   - {autoclasses[found]}""")
            exit(1)
        autoclasses[found] = rst

class_keys = set(classes.keys())
autoclass_keys = set(autoclasses.keys())


print('-'*30)
print("Not in .rst files")
print_dict = {}
for item in class_keys.difference(autoclass_keys):
    src = classes[item]
    if src.name not in print_dict:
        print_dict[src.name] = []
    print_dict[src.name].append(item)
pprint(print_dict)

print('-'*30)
print("Inexistent in .py")
print_dict = {}
for item in autoclass_keys.difference(class_keys):
    src = autoclasses[item]
    if src.name not in print_dict:
        print_dict[src.name] = []
    print_dict[src.name].append(item)
pprint(print_dict)
