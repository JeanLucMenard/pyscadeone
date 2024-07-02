# %%
import pytest
from pathlib import Path

from ansys.scadeone import ScadeOne, __version__, version_info
from ansys.scadeone.common.versioning import FormatVersions
from ansys.scadeone.common.storage import SwanFile, SwanString

class TestApp():
    def test_app(self):
        app = ScadeOne()
        assert app is not None

    def test_app_with(self):
        # check as container
        with ScadeOne() as app:
            assert app.version == __version__

    def test_app_with_exc(self):
        # check as container with exception
        with pytest.raises(KeyError) as exc_info:
            with ScadeOne() as app:
                d = {}
                d['no_key']
        assert str(exc_info.value) == "'no_key'"

    def test_version(self):
        assert __version__ == ".".join(
            (
                version_info.major,
                version_info.minor,
                version_info.buildID
            )
        )
        assert FormatVersions['swan'] == "2024.0"

    @pytest.mark.parametrize(
            "source,expected",
            [
                ("", (None, None)),
                (f"""\
-- version: {FormatVersions['swan']}
/* some code */
__END__
{{
    "ModelTree": {{
        "Properties": {{
            "version": "{FormatVersions['info']}"
        }}
    }}
}}
                """, (FormatVersions['swan'], FormatVersions['info']))
            ]
    )
    def test_swan_version(self, source, expected):
        def check(storage):
            swan_ver = storage.swan_version
            info_ver = storage.model_tree_version
            assert (swan_ver, info_ver) == expected
        check(SwanString(source))
        file = Path('check_version.swan')
        file.write_text(source)
        check(SwanFile(file))
        file.unlink()
