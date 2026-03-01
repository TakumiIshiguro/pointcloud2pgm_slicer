import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "pointcloud2pgm_slicer")))
from loader import _resolve_input_files


def test_resolve_plain_slam_split_files(tmp_path):
    (tmp_path / "map_cloud10.pcd").write_text("dummy")
    (tmp_path / "map_cloud2.pcd").write_text("dummy")
    (tmp_path / "map_cloud1.pcd").write_text("dummy")

    resolved = _resolve_input_files(str(tmp_path))

    assert [p.name for p in resolved] == ["map_cloud1.pcd", "map_cloud2.pcd", "map_cloud10.pcd"]


def test_resolve_prefers_split_over_single(tmp_path):
    (tmp_path / "map_cloud.pcd").write_text("dummy")
    (tmp_path / "map_cloud0.pcd").write_text("dummy")
    (tmp_path / "map_cloud1.pcd").write_text("dummy")

    resolved = _resolve_input_files(str(tmp_path))

    assert [p.name for p in resolved] == ["map_cloud0.pcd", "map_cloud1.pcd"]


def test_resolve_single_file(tmp_path):
    p = tmp_path / "input.pcd"
    p.write_text("dummy")

    resolved = _resolve_input_files(str(p))

    assert resolved == [p]
