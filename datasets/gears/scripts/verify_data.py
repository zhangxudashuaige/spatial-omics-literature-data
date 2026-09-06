#!/usr/bin/env python3
"""
验证 GEARS 数据完整性和可用性。

检查:
- 数据文件是否存在
- AnnData 是否可读取
- condition/cell_type 字段是否满足 GEARS 要求
- 图文件是否存在
- 环境依赖是否可导入
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
GRAPH_DIR = BASE_DIR / "graphs"


def check_imports():
    """检查关键依赖是否可导入。"""
    print("=" * 60)
    print("依赖检查")
    print("=" * 60)

    packages = {
        "gears": "cell-gears",
        "anndata": "anndata",
        "scanpy": "scanpy",
        "scvi": "scvi-tools",
        "torch": "torch",
        "numpy": "numpy",
        "pandas": "pandas",
        "scipy": "scipy",
    }

    all_ok = True
    for pkg, pip_name in packages.items():
        try:
            __import__(pkg)
            print(f"  [OK] {pkg}")
        except ImportError:
            print(f"  [FAIL] {pkg} (pip install {pip_name})")
            all_ok = False

    # PyG
    try:
        import torch_geometric
        print(f"  [OK] torch_geometric")
    except ImportError:
        print(f"  [WARN] torch_geometric 未安装 (构图功能需要)")

    print()
    return all_ok


def check_data_files():
    """检查数据文件。"""
    print("=" * 60)
    print("数据文件检查")
    print("=" * 60)

    expected = {
        "Norman (GEARS processed)": DATA_DIR / "processed" / "norman",
        "Adamson (GEARS processed)": DATA_DIR / "processed" / "adamson",
        "Dixit (GEARS processed)": DATA_DIR / "processed" / "dixit",
        "GO OBO": DATA_DIR / "external" / "gene_ontology" / "go-basic.obo",
    }

    for name, path in expected.items():
        if path.exists():
            if path.is_dir():
                files = list(path.glob("**/*.h5ad"))
                print(f"  [OK] {name}: {len(files)} h5ad 文件")
            else:
                size_mb = path.stat().st_size / (1024 * 1024)
                print(f"  [OK] {name}: {size_mb:.1f} MB")
        else:
            print(f"  [MISSING] {name}: {path}")

    print()


def check_graphs():
    """检查图文件。"""
    print("=" * 60)
    print("图文件检查")
    print("=" * 60)

    for graph_type in ["coexpression", "go_similarity"]:
        gdir = GRAPH_DIR / graph_type
        if gdir.exists():
            files = list(gdir.glob("*"))
            has_data = any(f.suffix in [".csv", ".pt", ".npz"] for f in files)
            status = "已构建" if has_data else "目录存在但未构建"
            print(f"  [{graph_type}]: {status} ({len(files)} 文件)")
        else:
            print(f"  [{graph_type}]: 目录不存在")

    print()


def check_anndata_readable():
    """检查所有 h5ad 文件是否可读取。"""
    print("=" * 60)
    print("AnnData 可读性检查")
    print("=" * 60)

    h5ad_files = list(DATA_DIR.glob("**/*.h5ad"))
    if not h5ad_files:
        print("  [INFO] 未找到 h5ad 文件。请先下载数据。")
        print()
        return

    try:
        import anndata as ad
    except ImportError:
        print("  [ERROR] anndata 未安装")
        return

    for f in h5ad_files:
        try:
            adata = ad.read_h5ad(f)
            has_condition = "condition" in adata.obs.columns
            print(f"  [OK] {f.name}: {adata.shape}, condition={'是' if has_condition else '否'}")
        except Exception as e:
            print(f"  [FAIL] {f.name}: {e}")

    print()


def main():
    print()
    print("=" * 60)
    print("GEARS 数据验证")
    print("=" * 60)
    print(f"项目目录: {BASE_DIR}")
    print()

    imports_ok = check_imports()
    check_data_files()
    check_graphs()
    check_anndata_readable()

    print("=" * 60)
    print("验证总结")
    print("=" * 60)
    print(f"依赖完整: {'是' if imports_ok else '否'}")
    print()
    print("如数据缺失，请运行:")
    print("  python scripts/download_gears_processed.py --dataset norman")
    print("  python scripts/build_coexpression_graph.py --adata <path>")
    print()

    return 0 if imports_ok else 1


if __name__ == "__main__":
    sys.exit(main())
