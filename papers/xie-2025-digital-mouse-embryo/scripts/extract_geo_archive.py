"""安全提取 GSE278603 TAR 中的六个官方 H5AD。"""

from __future__ import annotations

import argparse
import json
import tarfile
from pathlib import Path

EXPECTED = {
    "GSM9046243_Embryo_E7.5_stereo_rep1.h5ad",
    "GSM9046244_Embryo_E7.5_stereo_rep2.h5ad",
    "GSM9046245_Embryo_E7.75_stereo_rep1.h5ad",
    "GSM9046246_Embryo_E7.75_stereo_rep2.h5ad",
    "GSM9046247_Embryo_E8.0_stereo_rep1.h5ad",
    "GSM9046248_Embryo_E8.0_stereo_rep2.h5ad",
}


def safe_members(archive: tarfile.TarFile, output: Path) -> list[tarfile.TarInfo]:
    root = output.resolve()
    selected: list[tarfile.TarInfo] = []
    for member in archive.getmembers():
        if not member.isfile() or Path(member.name).name not in EXPECTED:
            continue
        target = (output / Path(member.name).name).resolve()
        if root not in target.parents:
            raise ValueError(f"不安全 TAR 成员路径：{member.name}")
        selected.append(member)
    return selected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--archive", type=Path, default=Path("data/external/GSE278603/GSE278603_RAW.tar")
    )
    parser.add_argument(
        "--output", type=Path, default=Path("data/external/GSE278603/h5ad")
    )
    parser.add_argument(
        "--report", type=Path, default=Path("results/reports/extraction_status.json")
    )
    args = parser.parse_args()
    if not args.archive.exists():
        raise FileNotFoundError(f"找不到 TAR：{args.archive}")
    args.output.mkdir(parents=True, exist_ok=True)
    extracted: list[dict[str, object]] = []
    with tarfile.open(args.archive, "r:*") as archive:
        members = safe_members(archive, args.output)
        found = {Path(m.name).name for m in members}
        missing = sorted(EXPECTED - found)
        if missing:
            raise RuntimeError(f"TAR 缺少预期文件：{missing}")
        for member in members:
            source = archive.extractfile(member)
            if source is None:
                raise RuntimeError(f"无法读取 TAR 成员：{member.name}")
            target = args.output / Path(member.name).name
            with source, target.open("wb") as sink:
                while chunk := source.read(8 * 1024 * 1024):
                    sink.write(chunk)
            extracted.append({"file": target.name, "size_bytes": target.stat().st_size})
    report = {"ok": True, "archive": str(args.archive), "files": extracted}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
