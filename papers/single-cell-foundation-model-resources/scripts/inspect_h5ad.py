#!/usr/bin/env python3
"""以backed模式检查本地H5AD结构。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--json", type=Path, dest="json_path")
    args = parser.parse_args()
    if not args.path.is_file():
        raise SystemExit(f"文件不存在：{args.path}")

    try:
        import anndata as ad
        import scipy.sparse as sp
    except ImportError as exc:
        raise SystemExit("缺少H5AD检查依赖；请先运行 pip install -r requirements.txt") from exc

    adata = ad.read_h5ad(args.path, backed="r")
    x = adata.X
    summary = {
        "path": str(args.path.resolve()),
        "shape": list(adata.shape),
        "x_type": type(x).__name__,
        "x_dtype": str(getattr(x, "dtype", "unknown")),
        "x_sparse": bool(sp.issparse(x) or "sparse" in type(x).__name__.lower()),
        "obs_columns": list(map(str, adata.obs.columns)),
        "var_columns": list(map(str, adata.var.columns)),
        "obsm_keys": list(map(str, adata.obsm.keys())),
        "uns_keys": list(map(str, adata.uns.keys())),
        "layers_keys": list(map(str, adata.layers.keys())),
        "raw_present": adata.raw is not None,
        "obs_names_sample": list(map(str, adata.obs_names[:5])),
        "var_names_sample": list(map(str, adata.var_names[:5])),
    }
    rendered = json.dumps(summary, ensure_ascii=False, indent=2)
    print(rendered)
    if args.json_path:
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(rendered + "\n", encoding="utf-8")
    if getattr(adata, "file", None) is not None:
        adata.file.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
