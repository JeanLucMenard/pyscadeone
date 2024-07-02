# %%
from pathlib import Path
from typing import cast
from ansys.scadeone import ScadeOne, ProjectFile

app = ScadeOne()

script_dir = Path(__file__).parents[1]
cc_project = script_dir / "examples/models/CC/CruiseControl/CruiseControl.sproj"

# %%
app.load_project(cc_project)

asset = ProjectFile(cc_project)
CC = app.load_project(asset)


# %%
projects = app.projects
assert len(projects) == 2
assert (
    cast(ProjectFile, projects[0].storage).source
    ==                                              # noqa: W504
    cast(ProjectFile, projects[1].storage).source)

# %%
model = CC.model

import ansys.scadeone.swan as S

def op_filter(obj: S.GlobalDeclaration):
    if isinstance(obj, S.Operator):
        return str(obj.identifier) == 'Regulation'
    return False

decl = model.find_declaration(op_filter)

# %%
op = cast(S.Operator, decl)
first_input = str(op.inputs[0].identifier)

assert first_input == 'CruiseSpeed'
assert model.all_modules_loaded == False

# %%
def type_filter(obj: S.GlobalDeclaration):
    return isinstance(obj, S.TypeDeclarations)

types = model.filter_declarations(type_filter)
count = len(list(types))

assert count == 5

type_list = list(model.types())
assert type_list[4].get_full_path() == "CC::tCruiseState"

assert model.all_modules_loaded

# %%
print("Smoke test: all done.")