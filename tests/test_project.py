import pytest
from typing import cast
from pathlib import Path
from ansys.scadeone import ScadeOne, ProjectFile


class TestProject():
    def test_wrong_project(self):
        app = ScadeOne()
        asset = ProjectFile("foo")
        project = app.load_project(asset)
        assert project is None

    def test_assets(self, cc_project):
        app = ScadeOne()
        asset = ProjectFile(cc_project)
        project = app.load_project(asset)
        sources = [swan.source for swan in project.swan_sources()]
        assert sources == [
            'examples/models/CC/CruiseControl/assets/CarTypes.swani',
            'examples/models/CC/CruiseControl/assets/CC.swan'
        ]

    def tests_all_assets(self, cc_project):
        app = ScadeOne()
        asset = ProjectFile(cc_project)
        project = app.load_project(asset)
        sources = [swan.source for swan in project.all_swan_sources()]
        assert sources == [
            'examples/models/CC/CruiseControl/assets/CarTypes.swani',
            'examples/models/CC/CruiseControl/assets/CC.swan',
            'examples/models/CC/CruiseControl/../utils/assets/Utils.swan'
        ]

    def test_project_assets(self, cc_project):
        app = ScadeOne()
        asset = cc_project
        p1 = app.load_project(asset)
        asset = Path(cc_project)
        p2 = app.load_project(asset)
        asset = ProjectFile(cc_project)
        p3 = app.load_project(asset)
        assert cast(ProjectFile, p1.asset).source == cast(ProjectFile, p2.asset).source
        assert cast(ProjectFile, p1.asset).source == cast(ProjectFile, p3.asset).source

    @pytest.mark.skip("Not yet implemented")
    def test_jobs(self, cc_project):
        app = ScadeOne()
        asset = ProjectFile(cc_project)
        project = app.load_project(asset)
        sources = [swan.source for swan in project.all_swan_sources()]
