# SPDX-FileCopyrightText: 2025 Ryo Funai
# SPDX-License-Identifier: Apache-2.0

"""
バックグラウンドで点群を読み込む
"""
from pathlib import Path
import re
from typing import List

import numpy as np
import open3d as o3d
from PyQt5 import QtCore


_MAP_CLOUD_INDEXED_RE = re.compile(r"^map_cloud(\d+)\.pcd$")


def _resolve_input_files(input_path: str) -> List[Path]:
    """Resolve one or more point-cloud files from a file path or directory path."""
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"入力パスが存在しません: {input_path}")

    if path.is_file():
        return [path]

    if not path.is_dir():
        raise ValueError(f"入力パスはファイルまたはディレクトリである必要があります: {input_path}")

    indexed_map_files = []
    for child in path.iterdir():
        if not child.is_file():
            continue
        matched = _MAP_CLOUD_INDEXED_RE.match(child.name)
        if matched:
            indexed_map_files.append((int(matched.group(1)), child))

    if indexed_map_files:
        indexed_map_files.sort(key=lambda x: x[0])
        return [entry[1] for entry in indexed_map_files]

    single_map_file = path / "map_cloud.pcd"
    if single_map_file.is_file():
        return [single_map_file]

    supported_ext = {".pcd", ".ply"}
    candidates = [
        child for child in path.iterdir()
        if child.is_file() and child.suffix.lower() in supported_ext
    ]

    if not candidates:
        raise FileNotFoundError(
            f"対応する点群ファイル(.pcd/.ply)が見つかりません: {input_path}"
        )

    return sorted(candidates)


class PointCloudLoaderThread(QtCore.QThread):
    loaded = QtCore.pyqtSignal(object)
    error = QtCore.pyqtSignal(str)

    def __init__(self, input_file: str, parent=None) -> None:
        super().__init__(parent)
        self.input_file = input_file

    def run(self) -> None:
        try:
            input_files = _resolve_input_files(self.input_file)

            point_arrays = []
            for point_file in input_files:
                pcd = o3d.io.read_point_cloud(str(point_file))
                if not pcd.has_points():
                    continue
                point_arrays.append(np.asarray(pcd.points))

            if not point_arrays:
                self.error.emit(f"点群が存在しません: {self.input_file}")
                return

            merged_points = np.vstack(point_arrays)
            merged_cloud = o3d.geometry.PointCloud()
            merged_cloud.points = o3d.utility.Vector3dVector(merged_points)

            # 生の点群をそのままemit（描画用のダウンサンプリングはModel側で実施）
            self.loaded.emit(merged_cloud)
        except Exception as e:
            self.error.emit(str(e))
