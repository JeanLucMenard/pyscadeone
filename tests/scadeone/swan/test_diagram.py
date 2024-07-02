# %%
from typing import cast, Union, Iterator

import pytest

import ansys.scadeone.swan as S
from ansys.scadeone import ScadeOne
from ansys.scadeone.common.storage import SwanString
from ansys.scadeone.model.loader import SwanParser
from ansys.scadeone.swan import Operator


@pytest.fixture
def parser(unit_test_logger):
    return SwanParser(unit_test_logger)


class TestDiagNav:

    @pytest.fixture
    def model(self, cc_project):
        app = ScadeOne()
        return app.load_project(cc_project).model

    @pytest.fixture
    def regulation(self, model):
        def regulation_filter(obj: S.GlobalDeclaration):
            if isinstance(obj, S.Operator):
                return str(obj.identifier) == "Regulation"
            return False

        return model.find_declaration(regulation_filter)

    @staticmethod
    def _get_block_expr(expr: S.Expression, diagram) -> Union[Iterator[S.ExprBlock], None]:
        for obj in diagram.objects:
            if not isinstance(obj, S.ExprBlock):
                continue
            if not isinstance(obj.expr, expr):
                continue
            yield obj

    @staticmethod
    def _get_binary_expr_block(
        binary_op: S.BinaryOp, diagram
    ) -> Union[Iterator[S.ExprBlock], None]:
        blocks = TestDiagNav._get_block_expr(S.BinaryExpr, diagram)
        for block in blocks:
            if block.expr.operator == binary_op:
                yield block

    def test_block(self, regulation):
        diagram = list(regulation.diagrams())[0]
        block = next(filter(lambda obj: isinstance(obj, S.Block), diagram.objects))
        assert str(block) == "(#28 block (SaturateThrottle))"

        sources = block.sources()
        assert len(sources) == 1
        (blk, conn) = sources[0]
        assert str(blk).find("(#25 expr #26 + #27") == 0

        targets = block.targets()
        assert len(targets) == 2
        (blk, conn) = targets[0]
        assert str(blk) == "(#29 def Throttle)"
        (blk, conn) = targets[1]
        assert str(blk.expr) == "#31 pre #32"

    def test_op_with_binary_expr(self, regulation):
        diagram = list(regulation.diagrams())[0]
        blocks = TestDiagNav._get_binary_expr_block(S.BinaryOp.Minus, diagram)
        block = next(blocks, None)
        assert block is not None

        sources = block.sources()
        assert len(sources) == 2
        (blk, conn) = sources[0]
        assert str(blk) == "(#0 expr CruiseSpeed)"
        (blk, conn) = sources[1]
        assert str(blk) == "(#1 expr CarSpeed)"

        targets = block.targets()
        assert len(targets) == 2
        (blk, conn) = targets[0]
        assert str(blk.expr) == "#6 * #7"
        (blk, conn) = targets[1]
        assert str(blk.expr) == "if #10 then #11 else #12"

    def test_op_with_ifte_expr(self, regulation):
        diagram = list(regulation.diagrams())[0]
        blocks = TestDiagNav._get_block_expr(S.IfteExpr, diagram)
        block = next(blocks, None)
        assert block is not None

        sources = block.sources()
        assert len(sources) == 3
        (blk, conn) = sources[0]
        assert str(blk.expr) == "#31 pre #32"
        (blk, conn) = sources[1]
        assert str(blk) == "(#13 expr SpeedZero)"
        (blk, conn) = sources[2]
        assert str(blk.expr) == "#3 - #4"

        targets = block.targets()
        assert len(targets) == 1
        (blk, conn) = targets[0]
        assert str(blk.expr) == "#15 + #16"

    def test_group(self, parser: SwanParser):
        code = SwanString(
            """
            inline function operator0 (i0: int32;
                                       i1: int32;)
              returns (o0: int32;)
            {
              diagram
                (#0 group)
                (#1 expr i0)
                (#2 group byname)
                (#3 group bypos)
                (#4 def o0)
                (#5 group)
                (#12 expr i1)
                
                (#6 wire #1 => #0 .(a))
                (#7 wire #0 => #2)
                (#8 wire #0 => #3)
                (#9 wire #2 => #5)
                (#10 wire #5 .(a) => #4)
                (#11 wire #3 => #5)
                (#13 wire #12 => #0 .(b))
            }
            """,
            "test_group",
        )
        (body, info) = parser.module_body(code)
        op = next(body.declarations)
        assert isinstance(op, Operator)
        diagram = list(op.diagrams())[0]
        assert len(diagram.objects) == 14

        group = diagram.objects[0]
        sources = group.sources()
        assert len(sources) == 2
        (blk, conn) = sources[0]
        assert str(blk) == "(#1 expr i0)"
        (blk, conn) = sources[1]
        assert str(blk) == "(#12 expr i1)"
        targets = group.targets()
        assert len(targets) == 2
        (blk, conn) = targets[0]
        assert str(blk) == "(#2 group byname)"
        assert conn is None
        (blk, conn) = targets[1]
        assert str(blk) == "(#3 group bypos)"
        assert conn is None

        i0 = diagram.objects[1]
        targets = i0.targets()
        assert len(targets) == 1
        (blk, conn) = targets[0]
        assert str(blk) == "(#0 group )"
        assert str(conn) == ".(a)"

        byname = diagram.objects[2]
        sources = byname.sources()
        assert len(sources) == 1
        (blk, conn) = sources[0]
        assert str(blk) == "(#0 group )"
        assert conn is None
        targets = byname.targets()
        assert len(targets) == 1
        (blk, conn) = targets[0]
        assert str(blk) == "(#5 group )"
        assert conn is None
