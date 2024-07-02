#! /bin/env python
"""
Check classes in .rst vs classes in .py, and produce a report on stdout
Usage: python autoclass.py
"""

import re
from pathlib import Path
from pprint import pformat
from itertools import chain
import logging

logging.basicConfig(filename="check_class.log", level=logging.DEBUG)

topDir = Path(__file__).parents[1]
srcPath = (topDir / "src").absolute()
rstPath = (topDir / 'doc' / 'source').absolute()

autodocRE = re.compile(r"""^(?P<comment>\.\.)? # commented directive
                       \s*\.\.\s+(?P<dir>autoclass|automodule|currentmodule)::
                       \s*(?P<item>\S+)\s*$""", # noqa
                       re.M | re.X)
pyClassRE = re.compile(r'^class\s+(\w+)\s*[:(]', re.M)


def cls_full_name(module, *classes):
    "helper: returns an iterable with module.class items "
    return [f"{module}.{cls}" for cls in classes]

# Documented with .. automodule:: directive
automodule = { key: 0 for key in ('ansys.scadeone.model.information',
                                  'ansys.scadeone.common.logger',
                                  'ansys.scadeone.common.exception',
                                  'ansys.scadeone.common.versioning') }

# Classes that are not documented in documentation
# chain() flattens a list of iterables
skipped_classes = {
    key: 0 for key in
    chain(
        # some loader classes
        cls_full_name('ansys.scadeone.model.loader',
                      'SwanParser',
                      'ParserLogger'),
        # storage base class
        cls_full_name('ansys.scadeone.common.storage',
                      'Storage',
                      'FileStorage',
                      'JobStorage',
                      'JobFile',
                      'JSONStorage',
                      'ProjectStorage',
                      'StringStorage',
                      'SwanStorage',
                      'SwanString'),
        # Misc.
        ('ansys.scadeone.scadeone.IScadeOne',
         'ansys.scadeone.project.IProject'),
    )
}

# Extract classes from Sources
logging.debug("### Python analyze")
py_classes = {}
for py in srcPath.glob('**/*.py'):
    # skip automodule files
    module_parts = re.sub(r'.*\\src\\', '', str(py)).removesuffix('.py').split('\\')
    if module_parts[-2] == 'swan':
        module_parts.pop() # keep only the swan part, as __init__ import language
    module = '.'.join(module_parts)

    logging.debug("Python module: " + module)

    if module in automodule:
        logging.debug("Skip module: " + module)
        continue

    for found in pyClassRE.findall(py.read_text()):
        cls_name = f"{module}.{found}"
        if cls_name in skipped_classes:
            logging.debug("Skip: "+cls_name)
            skipped_classes[cls_name] += 1
            continue
        # no clash, as name contains the module path
        py_classes[cls_name] = py.relative_to(srcPath).name

logging.debug("Classes in Python:")
logging.debug(pformat(py_classes))

# Extract classes from .rst
logging.debug("### Documentation analyze")
rst_classes = {}
commented = []
module = ''
for rst in rstPath.glob('**/*.rst'):
    logging.debug(f"RST: {rst}")
    for found in autodocRE.finditer(rst.read_text()):
        # commented directive
        if found['comment']:
            commented.append(found['item'])

        # currentmodule directive
        if found['dir'] == 'currentmodule':
            module = found['item']
            logging.debug(f"Current module: {module}")
            continue

        # autoclass directive
        if found['dir'] == 'autoclass':
            cls_name = found['item']
            # class with no module name
            if cls_name.find('.') == -1:
                cls_name = f"{module}.{cls_name}"
            logging.debug(cls_name)
            # class may appear in several .rst
            rst_classes.setdefault(cls_name, []).append(rst.relative_to(rstPath).name)
            continue

        # automodule directive
        if found['dir'] == 'automodule':
            file = found['item']
            automodule[file] = automodule.get(file, 0) + 1


logging.debug("Classes in Rst:")
logging.debug(pformat(rst_classes))

# Report
print('='*30)
print("# General checks")
print('-'*30)
print('## Skipped classes (should not be in .rst)')
print(*sorted(skipped_classes.keys()), sep="\n")

print('-'*30)
print("## Commented directives (in .rst but commented)")
if commented:
    print(*commented, sep="\n")

print('-'*30)
print("## Automodule check (expected ..automodule directive)")
automodule_error = False
for mod, count in automodule.items():
    if count != 1:
        print(f"{mod}: {count} directives found")
        automodule_error = True
if not automodule_error:
    print('OK.')

print('-'*30)
print("## Multiple class references in doc check")
multiple_refs = False
for cls, rst in rst_classes.items():
    if len(rst) > 1:
        multiple_refs = True
        print(cls, *rst, sep='\n  ')
if multiple_refs is False:
    print("OK.")


class_keys = set(py_classes.keys())
autoclass_keys = set(rst_classes.keys())

print('='*30)
print("# Python vs doc checks")
# Check classes not in .rst
print('-'*30)
print('## Classes only in .py check')
source_dict = {}
for cls in class_keys.difference(autoclass_keys):
    src = py_classes[cls]
    if src not in source_dict:
        source_dict[src] = []
    source_dict[src].append(cls)
if source_dict:
    for src, cls in source_dict.items():
        print(src, *cls, sep="\n   ")
else:
    print("OK.")

# Check classes in .rst, but not in .py
print('-'*30)
print("## Classes only in .rst check")
source_dict = {}
for cls in autoclass_keys.difference(class_keys):
    src = rst_classes[cls][0] # should be one occurrence
    if src not in source_dict:
        source_dict[src] = []
    source_dict[src].append(cls)
if source_dict:
    for src, cls in source_dict.items():
        print(src, *cls, sep="\n   ")
else:
    print("OK.")

# That's all folks
