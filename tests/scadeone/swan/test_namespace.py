# Copyright (c) 2024 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.

from typing import List

import pytest

from ansys.scadeone import ScadeOne
from ansys.scadeone.common.storage import SwanString
from ansys.scadeone.model import Model
from ansys.scadeone.model.loader import SwanParser
import ansys.scadeone.swan as swan


@pytest.fixture
def parser(unit_test_logger):
    return SwanParser(unit_test_logger)


@pytest.fixture
def cc_module(cc_project):
    app = ScadeOne()
    app.load_project(cc_project)
    project = app.projects[0]
    model = project.model
    model.load_all_modules()
    modules = list(model.modules)
    return modules[1]


class TestModuleNamespace:

    def test_module_get_group_decl(self, parser: SwanParser):
        code = SwanString("group group0 = (int32, int32);", "test_group")
        (body, info) = parser.module_body(code)
        decl = body.get_declaration("group0")
        assert isinstance(decl, swan.GroupDecl)
        assert decl.identifier.value == "group0"

    def test_get_const_from_interface(self, parser: SwanParser):
        code = SwanString(
            """
                const const0: int32 = 0;
             """,
            "module0",
        )
        (interface, info) = parser.module_interface(code)
        const0 = interface.get_declaration("const0")
        assert isinstance(const0, swan.ConstDecl)
        assert const0.identifier.value == "const0"

    def test_module_get_type_decl(self, cc_module):
        decl = cc_module.get_declaration("tCruiseState")
        assert isinstance(decl, swan.TypeDecl)
        assert decl.identifier.value == "tCruiseState"

    def test_module_get_const_decl(self, cc_module):
        decl = cc_module.get_declaration("SpeedInc")
        assert isinstance(decl, swan.ConstDecl)
        assert decl.identifier.value == "SpeedInc"

    def test_module_get_sensor_decl(self, cc_module):
        decl = cc_module.get_declaration("Ki")
        assert isinstance(decl, swan.SensorDecl)
        assert decl.identifier.value == "Ki"

    def test_module_get_op_decl(self, cc_module):
        decl = cc_module.get_declaration("Regulation")
        assert isinstance(decl, swan.Operator)
        assert decl.identifier.value == "Regulation"


class TestScopeNamespace:

    @staticmethod
    def _create_model(modules: List[swan.Module]):
        model = Model()
        for module in modules:
            model._modules[module.name] = module
            module.owner = model
        return model

    def test_get_const(self, parser: SwanParser):
        code = SwanString(
            """
                const const0: int32 = 0;

                node operator0 (i0: int32;)
                  returns (o0: int32;)
                {
                  diagram
                    (#0 expr const0)
                    (#1 def o0)
                    (#2 wire #0 => #1)
                }
                """,
            "module0",
        )
        (body, info) = parser.module_body(code)
        op0 = body.declaration_list[1]
        assert isinstance(op0, swan.Operator)
        scope = op0.body
        const0 = scope.get_declaration("const0")
        assert isinstance(const0, swan.ConstDecl)
        assert const0.identifier.value == "const0"

    def test_get_sensor(self, parser: SwanParser):
        code = SwanString(
            """
                sensor sensor0: int32;

                node operator0 (i0: int32;)
                  returns (o0: int32;)
                {
                  diagram
                    (#0 expr sensor0)
                    (#1 def o0)
                    (#2 wire #0 => #1)
                }
                """,
            "module0",
        )
        (body, info) = parser.module_body(code)
        op0 = body.declaration_list[1]
        assert isinstance(op0, swan.Operator)
        scope = op0.body
        sensor0 = scope.get_declaration("sensor0")
        assert isinstance(sensor0, swan.SensorDecl)
        assert sensor0.identifier.value == "sensor0"

    def test_get_op(self, parser: SwanParser):
        code = SwanString(
            """
                function operator0 (i0: int32;)
                  returns (o0: int32;)
                {
                  diagram
                    (#0 def o0)
                    (#5 expr i0)
                    (#6 wire #5 => #0)
                }

                node operator1 (i0: int32;)
                  returns (o0: int32;)
                {
                  diagram
                    (#0 block (operator0))
                    (#1 def o0)
                    (#2 expr i0)
                    (#3 wire #2 => #0 .(i0))
                    (#4 wire #0 .(o0) => #1)
                }
                """,
            "module0",
        )
        (body, info) = parser.module_body(code)
        op1 = body.declaration_list[1]
        assert isinstance(op1, swan.Operator)
        scope = op1.body
        op0 = scope.get_declaration("operator0")
        assert isinstance(op0, swan.Operator)
        assert op0.identifier.value == "operator0"

    def test_get_input(self, parser: SwanParser):
        code = SwanString(
            """
                function operator0 (i0: int32;)
                  returns (o0: int32;)
                {
                  diagram
                    (#0 def o0)
                    (#5 expr i0)
                    (#6 wire #5 => #0)
                }
                """,
            "module0",
        )
        (body, info) = parser.module_body(code)
        op0 = body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope = op0.body
        i0 = scope.get_declaration("i0")
        assert isinstance(i0, swan.VarDecl)
        assert i0.identifier.value == "i0"

    def test_get_output(self, parser: SwanParser):
        code = SwanString(
            """
                function operator0 (i0: int32;)
                  returns (o0: int32;)
                {
                  diagram
                    (#0 def o0)
                    (#5 expr i0)
                    (#6 wire #5 => #0)
                }
                """,
            "module0",
        )
        (body, info) = parser.module_body(code)
        op0 = body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope = op0.body
        o0 = scope.get_declaration("o0")
        assert isinstance(o0, swan.VarDecl)
        assert o0.identifier.value == "o0"

    def test_get_local(self, parser: SwanParser):
        code = SwanString(
            """
                node operator0 (i0: int32;)
                  returns (o0: int32;)
                {
                  diagram
                    (#0 def o0)
                    (#1 expr x0)
                    (#2 wire #1 => #0)
                    (#3 var x0:int32;)
                    (#4 let x0 = 1;)
                }
                """,
            "module0",
        )
        (body, info) = parser.module_body(code)
        op0 = body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope = op0.body
        x0 = scope.get_declaration("x0")
        assert isinstance(x0, swan.VarDecl)
        assert x0.identifier.value == "x0"

    def test_get_global(self, parser: SwanParser):
        code = SwanString(
            """
                node operator0 (i0: int32)
                returns (o0: int32)
                {
                  var x0: int32;
                  let x0 = 1;
                  diagram
                    (#0 def o0)
                    (#1 expr x0)
                    (#2 wire #1 => #0)
                }
                """,
            "module0",
        )
        (body, info) = parser.module_body(code)
        op0 = body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope = op0.body
        x0 = scope.get_declaration("x0")
        assert isinstance(x0, swan.VarDecl)
        assert x0.identifier.value == "x0"

    def test_get_used_op(self, parser: SwanParser):
        module0 = SwanString(
            """
            node operator0 (i0: int32;)
              returns (o0: int32;)
            {
              diagram
                (#0 expr i0)
                (#1 def o0)
                (#2 wire #0 => #1)
            }
            """,
            "module0",
        )
        module1 = SwanString(
            """
            use module0;
            
            node operator1 (i0: int32;)
              returns (o0: int32;)
            {
              diagram
                (#0 block (module0::operator0))
                (#1 expr i0)
                (#2 def o0)
                (#3 wire #1 => #0)
                (#4 wire #0 => #2)
            }
            """,
            "module1",
        )
        (module0_body, info) = parser.module_body(module0)
        (module1_body, info) = parser.module_body(module1)
        TestScopeNamespace._create_model([module0_body, module1_body])
        op1 = module1_body.declaration_list[0]
        assert isinstance(op1, swan.Operator)
        scope = op1.body
        op0 = scope.get_declaration("module0::operator0")
        assert isinstance(op0, swan.Operator)
        assert op0.identifier.value == "operator0"
        assert op0.module.name.name == "module0"

    def test_get_input_from_automaton(self, parser: SwanParser):
        code = SwanString(
            """
                node operator8 (i0: int32;)
                  returns (o0: int32;)
                {
                  diagram
                    (#0 let
                           automaton #automaton0
                           initial state #4 state0 :
                             diagram
                               (#1 expr i0)
                               (#2 def o0)
                               (#3 wire #1 => #2)
                           state #5 state1 :
                           :1: #4 until 
                           restart #5;
                    ;)
                }
                """,
            "module0",
        )
        (body, info) = parser.module_body(code)
        op0 = body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope_section = op0.body.sections[0].objects[0].section.equations[0].items[0].sections[0]
        i0 = scope_section.get_declaration("i0")
        assert isinstance(i0, swan.VarDecl)
        assert i0.identifier.value == "i0"

    def test_get_const_from_automaton(self, parser: SwanParser):
        code = SwanString(
            """
                const const0 : int32 = 0;
                node operator0 (i0: int32;)
                  returns (o0: int32;)
                {
                  diagram
                    (#0 let
                           automaton #automaton0
                           initial state #4 state0 :
                             diagram
                               (#1 expr i0)
                               (#2 def o0)
                               (#3 wire #1 => #2)
                           state #5 state1 :
                           :1: #4 until 
                           restart #5;
                    ;)
                }
                """,
            "module0",
        )
        (body, info) = parser.module_body(code)
        op0 = body.declaration_list[1]
        assert isinstance(op0, swan.Operator)
        scope_section = op0.body.sections[0].objects[0].section.equations[0].items[0].sections[0]
        const0 = scope_section.get_declaration("const0")
        assert isinstance(const0, swan.ConstDecl)
        assert const0.identifier.value == "const0"

    def test_get_global_from_diag(self, parser: SwanParser):
        code = SwanString(
            """
                node operator0 (i0: int32)
                returns (o0: int32)
                {
                  var x0: int32;
                  diagram
                    (let x0 = 1;)
                }
                """,
            "module0",
        )
        (body, info) = parser.module_body(code)
        op0 = body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope_section = op0.body.sections[1]
        x0 = scope_section.get_declaration("x0")
        assert isinstance(x0, swan.VarDecl)
        assert x0.identifier.value == "x0"

    def test_get_input_from_emit(self, parser: SwanParser):
        code = SwanString(
            """
                node operator0 (i0: int32)
                returns (o0: int32)
                {
                  diagram
                    (#0 var b:bool;)
                    (#1 emit 'b;)
                }
                """,
            "module0",
        )
        (body, info) = parser.module_body(code)
        op0 = body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope_section = op0.body.sections[0].objects[1].section
        b = scope_section.get_declaration("b")
        assert isinstance(b, swan.VarDecl)
        assert b.identifier.value == "b"

    def test_get_input_output_from_assume(self, parser: SwanParser):
        code = SwanString(
            """
                node operator0 (i0: int32)
                returns (o0: int32)
                {
                  diagram
                    (#0 assume i0_positive: i0 > 0;)
                    (#0 assume o0_positive: 0 < o0;)
                }
                """,
            "module0",
        )
        (body, info) = parser.module_body(code)
        op0 = body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope_section = op0.body.sections[0].objects[0].section
        i0 = scope_section.get_declaration("i0")
        assert isinstance(i0, swan.VarDecl)
        assert i0.identifier.value == "i0"
        scope_section = op0.body.sections[0].objects[1].section
        o0 = scope_section.get_declaration("o0")
        assert isinstance(o0, swan.VarDecl)
        assert o0.identifier.value == "o0"

    def test_get_input_from_guarantee(self, parser: SwanParser):
        code = SwanString(
            """
                node operator0 (i0: int32)
                returns (o0: int32)
                {
                  diagram
                    (#0 guarantee i0_positive: i0 > 0;)
                }
                """,
            "module0",
        )
        (body, info) = parser.module_body(code)
        op0 = body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope_section = op0.body.sections[0].objects[0].section
        i0 = scope_section.get_declaration("i0")
        assert isinstance(i0, swan.VarDecl)
        assert i0.identifier.value == "i0"

    def test_get_input_from_forward(self, parser: SwanParser):
        code = SwanString(
            """
                function operator0 (i0: int32;)
                  returns (o0: int32;)
                {
                  diagram
                    (#0 def o0)
                    (#5 expr i0)
                    (#6 wire #5 => #0)
                }
                
                function operator1 (A: int32^10)
                    returns (B: int32^10)
                    {
                        let B = 
                            forward <<10>> with [ai]=A;
                                let bi = operator0(ai);
                            returns ([bi]);
                    }
                """,
            "module0",
        )
        (body, info) = parser.module_body(code)
        op1 = body.declaration_list[1]
        assert isinstance(op1, swan.Operator)
        scope_section = op1.body.sections[0].equations[0].expr.body.body[0]
        op0 = scope_section.get_declaration("operator0")
        assert isinstance(op0, swan.Operator)
        assert op0.identifier.value == "operator0"

    def test_get_used_const(self, parser: SwanParser):
        module0 = SwanString(
            """
            const const0: int32 = 0;
            """,
            "module0",
        )
        module1 = SwanString(
            """
            use module0;

            node operator0 (i0: int32;)
              returns (o0: int32;)
            {
              diagram
                (#0 def o0)
                (#1 expr module0::const0)
                (#2 wire #1 => #0)
            }
            """,
            "module1",
        )
        (module0_body, info) = parser.module_body(module0)
        (module1_body, info) = parser.module_body(module1)
        TestScopeNamespace._create_model([module0_body, module1_body])
        op0 = module1_body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope_section = op0.body.sections[0]
        c0 = scope_section.get_declaration("module0::const0")
        assert isinstance(c0, swan.ConstDecl)
        assert c0.identifier.value == "const0"
        assert c0.module.name.name == "module0"

    def test_get_used_const_with_ns(self, parser: SwanParser):
        module0 = SwanString(
            """
            const const0: int32 = 0;
            """,
            "module0::module00",
        )
        module1 = SwanString(
            """
            use module0::module00;

            node operator0 (i0: int32;)
              returns (o0: int32;)
            {
              diagram
                (#0 def o0)
                (#1 expr module0::module00::const0)
                (#2 wire #1 => #0)
            }
            """,
            "module1",
        )
        (module0_body, info) = parser.module_body(module0)
        (module1_body, info) = parser.module_body(module1)
        TestScopeNamespace._create_model([module0_body, module1_body])
        op0 = module1_body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope_section = op0.body.sections[0]
        c0 = scope_section.get_declaration("module0::module00::const0")
        assert isinstance(c0, swan.ConstDecl)
        assert c0.identifier.value == "const0"
        assert c0.module.name.as_string == "module0::module00"

    def test_get_used_const_with_alias(self, parser: SwanParser):
        module0 = SwanString(
            """
            const const0: int32 = 0;
            """,
            "module0",
        )
        module1 = SwanString(
            """
            use module0 as m;

            node operator0 (i0: int32;)
              returns (o0: int32;)
            {
              diagram
                (#0 def o0)
                (#1 expr m::const0)
                (#2 wire #1 => #0)
            }
            """,
            "module1",
        )
        (module0_body, info) = parser.module_body(module0)
        (module1_body, info) = parser.module_body(module1)
        TestScopeNamespace._create_model([module0_body, module1_body])
        op0 = module1_body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope_section = op0.body.sections[0]
        c0 = scope_section.get_declaration("m::const0")
        assert isinstance(c0, swan.ConstDecl)
        assert c0.identifier.value == "const0"
        assert c0.module.name.name == "module0"

    def test_get_used_const_with_ns_and_alias(self, parser: SwanParser):
        module0 = SwanString(
            """
            const const0: int32 = 0;
            """,
            "module0::module00",
        )
        module1 = SwanString(
            """
            use module0::module00 as m;

            node operator0 (i0: int32;)
              returns (o0: int32;)
            {
              diagram
                (#0 def o0)
                (#1 expr m::const0)
                (#2 wire #1 => #0)
            }
            """,
            "module1",
        )
        (module0_body, info) = parser.module_body(module0)
        (module1_body, info) = parser.module_body(module1)
        TestScopeNamespace._create_model([module0_body, module1_body])
        op0 = module1_body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope_section = op0.body.sections[0]
        c0 = scope_section.get_declaration("module0::module00::const0")
        assert isinstance(c0, swan.ConstDecl)
        assert c0.identifier.value == "const0"
        assert c0.module.name.as_string == "module0::module00"

    def test_get__const_from_interface(self, parser: SwanParser):
        module0_int = SwanString(
            """
            const const0: int32 = 0;
            """,
            "module0",
        )
        module0 = SwanString(
            """
            node operator0 (i0: int32;)
              returns (o0: int32;)
            {
              diagram
                (#0 def o0)
                (#1 expr const0)
                (#2 wire #1 => #0)
            }
            """,
            "module0",
        )
        (module0_interface, info) = parser.module_interface(module0_int)
        (module0_body, info) = parser.module_body(module0)
        TestScopeNamespace._create_model([module0_interface, module0_body])
        op0 = module0_body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope_section = op0.body.sections[0]
        c0 = scope_section.get_declaration("const0")
        assert isinstance(c0, swan.ConstDecl)
        assert c0.identifier.value == "const0"
        assert c0.module.name.as_string == "module0"

    def test_get_input_from_anonymous_op(self, parser: SwanParser):
        code = SwanString(
            """
                function operator0 (i0: int32;)
                  returns (o0: int32;)
                {
                  diagram
                    (#0 def o0)
                    (#5 expr i0)
                    (#6 wire #5 => #0)
                }

                node operator1 (i0: int32;)
                  returns (o0: int32;)
                {
                  diagram
                    (#0 block (({op_expr%function i => operator0(i)%op_expr})))
                    (#1 expr i0)
                    (#2 def o0)
                    
                    (#3 wire #1 => #0 .(i))
                    (#4 wire #0 => #2)
                }
                """,
            "module0",
        )
        (body, info) = parser.module_body(code)
        op1 = body.declaration_list[1]
        assert isinstance(op1, swan.Operator)
        scope_section = op1.body.sections[0]
        op0 = scope_section.get_declaration("operator0")
        assert isinstance(op0, swan.Operator)
        assert op0.identifier.value == "operator0"

    def test_get_used_const_decl_interface(self, parser: SwanParser):
        imodule0 = SwanString(
            """
            const const0: int32 = 0;
            """,
            "module0",
        )
        module0 = SwanString(
            """
            """,
            "module0",
        )
        module1 = SwanString(
            """
            use module0;

            node operator0 (i0: int32;)
              returns (o0: int32;)
            {
              diagram
                (#0 def o0)
                (#1 expr module0::const0)
                (#2 wire #1 => #0)
            }
            """,
            "module1",
        )
        (module0_body, info) = parser.module_body(module0)
        (module0_interface, info) = parser.module_interface(imodule0)
        (module1_body, info) = parser.module_body(module1)
        TestScopeNamespace._create_model([module0_interface, module0_body, module1_body])
        op0 = module1_body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope_section = op0.body.sections[0]
        c0 = scope_section.get_declaration("module0::const0")
        assert isinstance(c0, swan.ConstDecl)
        assert c0.identifier.value == "const0"
        assert c0.module.name.name == "module0"

    def test_get_const_decl_interface(self, parser: SwanParser):
        imodule0 = SwanString(
            """
            const const0: int32 = 0;
            function operator0 (i0: int32)
              returns (o0: int32);
            """,
            "module0",
        )

        (module0_interface, info) = parser.module_interface(imodule0)
        op0 = module0_interface.declaration_list[1]
        assert isinstance(op0, swan.Signature)
        module = op0.module
        assert isinstance(module, swan.ModuleInterface)
        c0 = module.get_declaration("const0")
        assert isinstance(c0, swan.ConstDecl)
        assert c0.identifier.value == "const0"
        assert c0.module.name.name == "module0"

    def test_get_regulation_from_state(self, cc_module):
        automaton0 = cc_module.declaration_list[2].body.sections[0].objects[0].section.equations[0]
        automaton1 = automaton0.items[1].sections[0].objects[13].section.equations[0]
        automaton2 = automaton1.items[0].sections[0].objects[10].section.equations[0]
        scope_section = automaton2.items[0].sections[0]
        op = scope_section.get_declaration("Regulation")
        assert isinstance(op, swan.Operator)
        assert op.identifier.value == "Regulation"

    def test_get_limiter_from_cruise_speed_mng_op(self, cc_module):
        cruise_speed_mng_op = cc_module.declaration_list[3]
        scope_section = cruise_speed_mng_op.body.sections[0]
        op = scope_section.get_declaration("Utils::Limiter")
        assert isinstance(op, swan.Operator)
        assert op.identifier.value == "Limiter"
        assert op.module.name.name == "Utils"
