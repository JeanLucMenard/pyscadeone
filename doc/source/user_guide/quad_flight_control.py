from pathlib import Path
from typing import cast
from ansys.scadeone import ScadeOne
import ansys.scadeone.swan as S

# Update according to your installation
s_one_install = Path('C:/s-one')

quad_flight_project = (s_one_install
                       / 'examples/QuadFlightControl'
                       / 'QuadFlightControl.sproj')

app = ScadeOne()
project = app.load_project(quad_flight_project)

# Direct project dependencies
my_dependency = project.dependencies()

# All dependencies recursively
all_dependencies = project.dependencies(all=True)

# Direct project Swan sources
sources = project.swan_sources()

# All sources, including those from dependencies
all_sources = project.swan_sources(all=True)

# Get the model
model = project.model

# All sensors in the model
sensors = model.sensors()

# All operators in the model
operators = model.operator()


# Filter function, looking for an operator of name 'EngineControl'
def op_filter(obj: S.GlobalDeclaration):
    if isinstance(obj, S.Operator):
        return str(obj.identifier) == 'EngineControl'
    return False


# Get the operator
op_decl = model.find_declaration(op_filter)

# All Swan constructs have a path.
type_list = list(model.types())
print(type_list[1].get_full_path())  # => "QuadFlightControl::EngineHealth"

# Stating op_decl is indeed a Swan operator
operator = cast(S.Operator, op_decl)
print(f"first input: {operator.inputs[0].identifier}")  # => 'attitudeCmd'