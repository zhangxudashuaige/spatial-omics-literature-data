"""验证清单、样例主键、Notebook JSON 和代码单元可执行性。"""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DATASET_COLUMNS = {
    "dataset_id", "data_name", "modality", "sample_stage", "source", "accession",
    "download_url", "file_format", "file_size", "direct_download", "local_directory",
    "commit_to_github",
}
REQUIRED_FILE_COLUMNS = {
    "file_id", "dataset_id", "file_name_or_pattern", "download_url", "file_format",
    "file_size", "direct_download", "local_path", "commit_to_github", "sha256", "status",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    datasets_path = ROOT / "manifests" / "datasets.csv"
    files_path = ROOT / "manifests" / "files.csv"
    datasets = read_csv(datasets_path)
    files = read_csv(files_path)
    with datasets_path.open(encoding="utf-8-sig", newline="") as handle:
        dataset_columns = set(next(csv.reader(handle)))
    with files_path.open(encoding="utf-8-sig", newline="") as handle:
        file_columns = set(next(csv.reader(handle)))
    assert REQUIRED_DATASET_COLUMNS <= dataset_columns
    assert REQUIRED_FILE_COLUMNS <= file_columns
    assert len(datasets) >= 12
    assert len(files) >= 15
    assert len({row["dataset_id"] for row in datasets}) == len(datasets)
    assert len({row["file_id"] for row in files}) == len(files)
    dataset_ids = {row["dataset_id"] for row in datasets}
    assert all(row["dataset_id"] in dataset_ids for row in files)

    metadata = read_csv(ROOT / "data" / "sample" / "sample_cell_metadata.csv")
    assert len({row["cell_id"] for row in metadata}) == len(metadata)

    os.environ.setdefault("MPLBACKEND", "Agg")
    notebooks = sorted((ROOT / "notebooks").glob("0*.ipynb"))
    assert len(notebooks) == 5
    for notebook_path in notebooks:
        payload = json.loads(notebook_path.read_text(encoding="utf-8"))
        assert payload["nbformat"] == 4
        namespace = {"__name__": f"validation_{notebook_path.stem}"}
        for cell in payload["cells"]:
            if cell["cell_type"] != "code":
                continue
            source = "".join(cell["source"])
            compiled = compile(source, str(notebook_path), "exec")
            exec(compiled, namespace)
        print(f"Notebook 通过：{notebook_path.name}")

    print(f"清单通过：datasets={len(datasets)}，files={len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
