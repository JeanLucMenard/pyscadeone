import ansys.scadeone.swan as swan

from pathlib import Path
from typing import cast
from ansys.scadeone import ScadeOne

# Update according to your installation
s_one_install = Path(r'C:\Scade One')

quad_flight_project = (s_one_install
                       / 'examples/QuadFlightControl'
                       / 'QuadFlightControl.sproj')

app = ScadeOne()
model = app.load_project(quad_flight_project).model


def quad_fight_control_op_filter(obj: swan.GlobalDeclaration):
    if isinstance(obj, swan.Operator):
        return str(obj.identifier) == 'QuadFlightControl'
    return False


# Get the 'QuadFightControl' operator from model
quad_fight_control_op = cast(swan.Operator, model.find_declaration(quad_fight_control_op_filter))

# Get the diagram of the 'QuadFightControl' operator
diag = next(quad_fight_control_op.diagrams(), None)

# Get the diagram blocks ('MotorControl', 'FlightControl')
blocks = list(filter(lambda obj: isinstance(obj, swan.Block), diag.objects))

# Get the 'MotorControl' block
motor_control_block = next(filter(lambda block: block.instance.path_id.full_name == 'MotorControl', blocks))

# Get the 'MotorControl' sources ('FlightControl', 'motorStates')
sources = motor_control_block.sources()

# Get the 'MotorControl' targets ('motorHealthState', 'rotorCmd',  'byname' group)
targets = motor_control_block.targets()


print("The object diagram sources of 'MotorControl' operator are:")
print("-----------------------------------")
for block, adapt in sources:
    if isinstance(block, swan.ExprBlock):
        print(f"Operator name: {str(block.expr.id)}, Adaptation: {str(adapt)}")
    elif isinstance(block, swan.Block):
        print(f"Operator name: {str(block.instance.path_id)}, Adaptation: {str(adapt)}")
print("-----------------------------------")
print("")
print("The object diagram targets of 'MotorControl' operator are:")
print("-----------------------------------")
for block, adapt in targets:
    if isinstance(block, swan.DefBlock):
        print(f"Operator name: {str(block.lhs)}, Adaptation: {str(adapt)}")
    elif isinstance(block, swan.Bar):
        print(f"Operator name: {str(block.operation.name)}, Adaptation: {str(adapt)}")
print("-----------------------------------")


def motor_control_op_filter(obj: swan.GlobalDeclaration):
    if isinstance(obj, swan.Operator):
        return str(obj.identifier) == 'MotorControl'
    return False


# Get the 'MotorControl' operator from model
motor_control_op = cast(swan.Operator, model.find_declaration(motor_control_op_filter))

# Get the diagram of the 'MotorControl' operator
diag = next(motor_control_op.diagrams(), None)


def input_filter(obj: swan.DiagramObject):
    if not isinstance(obj, swan.ExprBlock):
        return False
    if not isinstance(obj.expr, swan.StructProjection):
        return False
    return str(obj.expr.expr.id) == 'attitudeCmd'


# Get the 'attitudeCmd' fields from the diagram (expression blocks)
objs = list(filter(lambda obj: input_filter(obj), diag.objects))


def contains_output(objs):
    return next(filter(lambda obj: isinstance(obj, swan.DefBlock), objs), None) is not None


# Get the blocks following the flows from the 'attitudeCmd' input to the 'rotorCmd' output
blocks = set()
while not contains_output(objs):
    targets = set()
    for obj in objs:
        for target in obj.targets():
            targets.add(target[0])
            if isinstance(target[0], swan.Block):
                blocks.add(target[0])
    objs = targets

print("")
print("In the 'MotorControl' operator, the 'attitudeCmd' input passes through the following object diagrams:")
print("-----------------------------------")
for source in blocks:
    if isinstance(source.instance, swan.PathIdOpCall):
        print(f"Operator name: {source.instance.path_id}")
    elif isinstance(source.instance, swan.PrefixOperatorExpression):
        print(f"Operator name: {source.instance.operator_expression.operator.path_id}")
        print(f"Instance name: {source.instance_name}")
    print("-----------------------------------")

