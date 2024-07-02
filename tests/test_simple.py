# %%
from ansys.scadeone import ScadeOne, __version__, version_info


class TestApp():
    def test_app(self):
        app = ScadeOne()
        assert app is not None

    def test_version(self):
        assert __version__ == ".".join(
            (
                version_info.major,
                version_info.minor,
                version_info.patch
            )
        )
