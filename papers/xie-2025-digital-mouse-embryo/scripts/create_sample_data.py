"""抽取许可确认后的真实样例，或创建仅供代码测试的合成 H5AD。"""

from __future__ import annotations

import argparse
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd
from scipy import sparse


MARKERS = ["Myl7", "Tnnt2", "Mef2c", "Shh", "Cer1", "Apela"]


def synthetic(output: Path, n_obs: int = 750) -> Path:
    rng = np.random.default_rng(278603)
    stages = np.repeat(["E7.5", "E7.75", "E8.0"], [250, 250, 250])[:n_obs]
    theta = np.linspace(0, 6 * np.pi, n_obs)
    x = np.cos(theta) * (1 + np.linspace(0, 1, n_obs)) + rng.normal(0, 0.08, n_obs)
    y = np.sin(theta) * (1 + np.linspace(0, 0.5, n_obs)) + rng.normal(0, 0.08, n_obs)
    z = np.linspace(0, 3, n_obs)
    genes = MARKERS + ["Actb", "Gapdh", "Sox2", "T"]
    values = rng.poisson(0.25, (n_obs, len(genes))).astype(np.float32)
    values[:, 0] += (x > 0.5) * rng.poisson(4, n_obs)
    values[:, 1] += (y > 0.5) * rng.poisson(4, n_obs)
    values[:, 4] += (stages == "E7.5") * rng.poisson(3, n_obs)
    obs = pd.DataFrame(
        {
            "stage": stages,
            "replicate": np.where(np.arange(n_obs) % 2 == 0, "rep1", "rep2"),
            "cell_type": np.where(x > 0.5, "cardiac_like", "other"),
            "germ_layer": np.where(y > 0, "mesoderm", "endoderm"),
            "cluster": np.where(x + y > 0, "0", "1"),
        },
        index=[f"synthetic_{i:04d}" for i in range(n_obs)],
    )
    var = pd.DataFrame(index=genes)
    adata = ad.AnnData(X=sparse.csr_matrix(values), obs=obs, var=var)
    adata.obsm["spatial"] = np.column_stack([x, y]).astype(np.float32)
    adata.obsm["spatial_3d"] = np.column_stack([x, y, z]).astype(np.float32)
    adata.layers["counts"] = adata.X.copy()
    adata.uns["notice"] = "完全合成的代码测试数据，不属于 GSE278603"
    output.parent.mkdir(parents=True, exist_ok=True)
    adata.write_h5ad(output, compression="gzip")
    return output


def subset_real(source: Path, output: Path, n_obs: int, confirm_license: bool) -> Path:
    if not confirm_license:
        raise PermissionError("未确认再分发许可；请核实后显式添加 --confirm-license")
    adata = ad.read_h5ad(source, backed="r")
    try:
        sample = adata[: min(n_obs, adata.n_obs)].to_memory().copy()
    finally:
        adata.file.close()
    sample.uns["source"] = "GSE278603"
    sample.uns["source_file"] = source.name
    output.parent.mkdir(parents=True, exist_ok=True)
    sample.write_h5ad(output, compression="gzip")
    size = output.stat().st_size
    if size >= 10 * 1024 * 1024:
        output.unlink()
        raise ValueError(f"样例为 {size} bytes，超过 10 MB，已撤销")
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--n-obs", type=int, default=750)
    parser.add_argument("--confirm-license", action="store_true")
    parser.add_argument("--synthetic", action="store_true")
    args = parser.parse_args()
    if args.synthetic:
        output = args.output or Path("data/processed/synthetic_test.h5ad")
        result = synthetic(output, args.n_obs)
    else:
        if args.source is None:
            args.source = Path("data/external/GSE278603/h5ad/GSM9046244_Embryo_E7.5_stereo_rep2.h5ad")
        output = args.output or Path("data/sample/GSE278603_sample_750_cells.h5ad")
        result = subset_real(args.source, output, args.n_obs, args.confirm_license)
    print(f"已生成：{result.resolve()} ({result.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
