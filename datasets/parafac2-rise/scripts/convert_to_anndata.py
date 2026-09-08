#!/usr/bin/env python3
"""将表达矩阵转换为稀疏 AnnData .h5ad，保留原始文件，记录转换过程。"""
import sys, argparse, json
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent.parent

def convert_csv_to_h5ad(input_path, output_path, is_raw_counts=None):
    try:
        import anndata
    except ImportError:
        print("[ERROR] anndata 未安装: pip install anndata")
        return False

    df = pd.read_csv(input_path, index_col=0)
    print(f"输入: {df.shape}")

    # 自动判断表达类型
    vals = df.values.flatten()[:10000]
    has_neg = (vals < 0).any()
    is_int = np.all(vals == vals.astype(int)) if vals.size > 0 else False
    if is_raw_counts is None:
        is_raw_counts = is_int and not has_neg
    expr_type = "raw_counts" if is_raw_counts else "normalized"
    print(f"表达类型: {expr_type}")

    # 假设行为基因、列为细胞（常见GEO格式）
    # 如果行数远大于列数，可能是细胞×基因
    if df.shape[0] > df.shape[1] * 10:
        print("[INFO] 检测到可能是细胞×基因格式，不转置")
        adata = anndata.AnnData(X=df.values, obs=pd.DataFrame(index=df.index), var=pd.DataFrame(index=df.columns))
    else:
        print("[INFO] 假设行为基因、列为细胞，转置为细胞×基因")
        adata = anndata.AnnData(X=df.T.values, obs=pd.DataFrame(index=df.columns), var=pd.DataFrame(index=df.index))

    adata.uns["expression_type"] = expr_type
    adata.uns["converted_from"] = str(input_path)
    adata.uns["converted_at"] = datetime.now().isoformat()
    adata.uns["conversion_note"] = "不将归一化表达误存成原始计数"

    adata.write_h5ad(output_path)
    print(f"[OK] 已保存: {output_path}")
    print(f"  形状: {adata.shape}")
    print(f"  X dtype: {adata.X.dtype}")
    return True

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--raw-counts", action="store_true", help="强制标记为原始计数")
    p.add_argument("--normalized", action="store_true", help="强制标记为归一化表达")
    args = p.parse_args()

    is_raw = None
    if args.raw_counts: is_raw = True
    if args.normalized: is_raw = False

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    success = convert_csv_to_h5ad(args.input, args.output, is_raw)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
