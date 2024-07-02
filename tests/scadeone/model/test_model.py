import pytest
from pathlib import Path  # noqa
from ansys.scadeone import ScadeOne
from ansys.scadeone.model import Model
import ansys.scadeone.swan as S
from ansys.scadeone.common.storage import SwanString
from ansys.scadeone.model.loader import SwanParser

from typing import cast


@pytest.fixture
def model(cc_project):
    app = ScadeOne()
    asset = cc_project
    project = app.load_project(asset)
    return project.model


@pytest.fixture
def parser(unit_test_logger):
    return SwanParser(unit_test_logger)


class TestModel:

    def test_model_creation(self, model: Model):
        assert model.all_modules_loaded == False

    def test_type_count(self, model: Model):
        def filter(obj: S.GlobalDeclaration):
            return isinstance(obj, S.TypeDeclarations)

        types = model.filter_declarations(filter)
        assert len(list(types)) == 5
        assert model.all_modules_loaded

    def test_find_regulation(self, model: Model):
        def filter(obj: S.GlobalDeclaration):
            if isinstance(obj, S.Operator):
                name = obj.identifier
                return str(obj.identifier) == "Regulation"
            return False

        decl = model.find_declaration(filter)
        assert decl is not None
        # DOES NOTHING AT RUNTIME, BUT TYPING KNOWS
        op = cast(S.Operator, decl)
        first = cast(S.VarDecl, op.inputs[0])
        assert str(first.identifier) == "CruiseSpeed"
        assert not model.all_modules_loaded

    def test_path(self, model: Model):
        types = list(model.types())
        assert len(types) == 5
        assert types[0].get_full_path() == "CarTypes::tPercent"
        assert types[1].get_full_path() == "CarTypes::tRpm"
        assert types[2].get_full_path() == "CarTypes::tSpeed"
        assert types[3].get_full_path() == "CarTypes::tTorq"
        assert types[4].get_full_path() == "CC::tCruiseState"

    def test_load_module(self, model):
        model.load_module("CC")
        modules = list(model.modules)
        assert len(modules) == 1
        cc_module = modules[0]
        assert str(cc_module.name) == "CC"


class TestInfo:
    @pytest.mark.parametrize(
        "data",
        [
            "",
            """
__END__
                """,
        ],
    )
    def test_no_data(self, data, parser: SwanParser, unit_test_logger):
        code = SwanString(
            f"""
            node operator0 (i0: int32;)
            returns (o0: int32;);
            {data}
            """,
            "test_no_END",
        )
        result = parser.module_body(code)
        if result[1].has_information:
            Path("err.log").write_text(f">>> {result[1]._info}")
        assert result[1].has_information is False

    def test_invalid_json(self, parser: SwanParser):
        code = SwanString(
            """
            node operator0 (i0: int32;)
            returns (o0: int32;);
            __END__
            [1, 2 , 4]
            """,
            "test_invalid_json",
        )
        result = parser.module_body(code)
        assert result[1].has_information is False

    def test_no_model_tree(self, parser: SwanParser):
        code = SwanString(
            """
            node operator0 (i0: int32;)
            returns (o0: int32;);
            __END__
            {
              "no_layout": { }
            }
            """,
            "test_valid_version",
        )
        result = parser.module_body(code)
        assert result[1].model_tree is None

    @pytest.mark.parametrize(
        "info",
        [
            '{"ModelTree": {}}',
            '{"ModelTree": {"Properties": {}}}',
            '{"ModelTree": {"Properties": {"version": null}}}',
        ],
    )
    def test_no_version(self, info, parser: SwanParser):
        code = SwanString(
            f"""
            node operator0 (i0: int32;)
            returns (o0: int32;);
            __END__
            {info}
            """,
            "test_valid_version",
        )
        result = parser.module_body(code)
        assert result[1].model_tree.version is None

    def test_valid_version(self, parser: SwanParser):
        code = SwanString(
            """
            node operator0 (i0: int32;)
            returns (o0: int32;);
            __END__
            {
              "ModelTree": {
                  "Children": {
                       "body[0]": {
                        }
                    },
                    "Properties": {
                        "version": "0.1.0"
                    }
                }
            }
            """,
            "test_valid_version",
        )
        result = parser.module_body(code)
        assert result[1].model_tree.version == "0.1.0"
