#!/usr/bin/env python3
"""检查四套官方模拟数据；默认不反序列化 pickle。"""
from __future__ import annotations

import argparse
import json
import pickle
import pickletools
from pathlib import Path

from inspect_h5ad import inspect as inspect_h5ad


def describe(value):
    import numpy as np
    if hasattr(value, "shape"):
        return {"type": type(value).__name__, "shape": list(value.shape), "dtype": str(getattr(value, "dtype", ""))}
    if isinstance(value, dict):
        return {str(k): describe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        try:
            arr = np.asarray(value)
            return {"type": type(value).__name__, "length": len(value), "shape": list(arr.shape), "unique_preview": list(map(str, np.unique(arr)[:20]))}
        except ValueError:
            return {"type": type(value).__name__, "length": len(value), "heterogeneous_items": [describe(v) for v in value[:20]]}
    return {"type": type(value).__name__, "repr": repr(value)[:300]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--trusted-pickle", action="store_true", help="only for files obtained from the pinned official commit")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = {"h5ad": {}, "pickle": {}}
    for path in sorted(args.path.rglob("*.h5ad")):
        report["h5ad"][str(path)] = inspect_h5ad(path)
    for path in sorted(args.path.rglob("*.pkl")):
        if args.trusted_pickle:
            with path.open("rb") as handle: value = pickle.load(handle)  # nosec B301 - opt-in and pinned official source only
            report["pickle"][str(path)] = describe(value)
        else:
            with path.open("rb") as handle: count = sum(1 for _ in pickletools.genops(handle))
            report["pickle"][str(path)] = {"status": "not_deserialized", "pickle_opcode_count": count}
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output: args.output.write_text(rendered, encoding="utf-8")
    print(rendered)


if __name__ == "__main__": main()
