#!/usr/bin/env python3
"""
统一基因标识。

不同队列可能使用不同的基因标识：
- Affymetrix 探针 ID
- Gene Symbol
- Entrez ID
- Ensembl ID

本脚本将所有基因标识统一转换为 Gene Symbol。

用法:
    python harmonize_gene_ids.py --input data/processed/GSE12251_series_matrix.txt.gz
    python harmonize_gene_ids.py --all
"""
import sys
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
METADATA_DIR = BASE_DIR / "data" / "metadata"


def detect_id_type(index):
    """检测基因标识类型。"""
    sample_ids = [str(x) for x in index[:100]]

    # Affymetrix 探针 ID (如 1007_s_at, AFFX-BioB-5_at)
    affy_count = sum(1 for x in sample_ids if "_at" in x or "_s_at" in x or "_x_at" in x or x.startswith("AFFX-"))
    if affy_count > len(sample_ids) * 0.3:
        return "affymetrix_probe"

    # Entrez ID (纯数字)
    entrez_count = sum(1 for x in sample_ids if x.isdigit())
    if entrez_count > len(sample_ids) * 0.8:
        return "entrez_id"

    # Ensembl ID (如 ENSG00000123456)
    ensembl_count = sum(1 for x in sample_ids if x.startswith("ENSG") or x.startswith("ENSMUSG"))
    if ensembl_count > len(sample_ids) * 0.3:
        return "ensembl_id"

    # Gene Symbol (如 TP53, BRCA1)
    return "gene_symbol"


def load_series_matrix(filepath):
    """加载 GEO series matrix。"""
    skip_rows = 0
    with open(filepath, "r", errors="replace") as f:
        for i, line in enumerate(f):
            if "series_matrix_table_begin" in line:
                skip_rows = i + 1
                break

    df = pd.read_csv(filepath, sep="\t", skiprows=skip_rows, index_col=0, low_memory=False)
    if df.index[-1] and "series_matrix_table_end" in str(df.index[-1]):
        df = df.iloc[:-1]
    return df


def harmonize_affymetrix(df, platform="GPL570"):
    """将 Affymetrix 探针 ID 转换为 Gene Symbol。

    注意：完整的探针注释需要从 GEO 下载平台注释文件。
    这里提供框架，实际转换需要平台注释文件。
    """
    print(f"[INFO] Affymetrix 探针转换需要平台注释文件 ({platform})")
    print(f"[INFO] 请从 GEO 下载平台注释: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={platform}")
    print(f"[INFO] 或使用 biomaRt / mygene 包进行转换")

    # 尝试使用 mygene（如果已安装）
    try:
        import mygene
        mg = mygene.MyGeneInfo()
        probes = list(df.index)
        print(f"[INFO] 使用 mygene 转换 {len(probes)} 个探针...")
        results = mg.querymany(probes, scopes="reporter", fields="symbol", species="human", verbose=False)
        mapping = {}
        for r in results:
            if "symbol" in r:
                mapping[r["query"]] = r["symbol"]
        df = df.rename(index=mapping)
        # 去除没有映射到 symbol 的探针
        df = df[df.index.notna() & (df.index != "")]
        # 对重复基因取均值
        df = df.groupby(df.index).mean()
        print(f"[OK] 转换完成: {len(df)} 个基因")
        return df
    except ImportError:
        print("[WARN] mygene 未安装，跳过探针转换。")
        print("[INFO] 安装: pip install mygene")
        return df
    except Exception as e:
        print(f"[ERROR] mygene 转换失败: {e}")
        return df


def harmonize_entrez(df):
    """将 Entrez ID 转换为 Gene Symbol。"""
    try:
        import mygene
        mg = mygene.MyGeneInfo()
        entrez_ids = [str(x) for x in df.index]
        print(f"[INFO] 使用 mygene 转换 {len(entrez_ids)} 个 Entrez ID...")
        results = mg.querymany(entrez_ids, scopes="entrezgene", fields="symbol", species="human", verbose=False)
        mapping = {}
        for r in results:
            if "symbol" in r:
                mapping[r["query"]] = r["symbol"]
        df = df.rename(index=mapping)
        df = df[df.index.notna() & (df.index != "")]
        df = df.groupby(df.index).mean()
        print(f"[OK] 转换完成: {len(df)} 个基因")
        return df
    except ImportError:
        print("[WARN] mygene 未安装，跳过 Entrez 转换。")
        return df
    except Exception as e:
        print(f"[ERROR] Entrez 转换失败: {e}")
        return df


def harmonize_ensembl(df):
    """将 Ensembl ID 转换为 Gene Symbol。"""
    try:
        import mygene
        mg = mygene.MyGeneInfo()
        ensembl_ids = [str(x).split(".")[0] for x in df.index]  # 去除版本号
        print(f"[INFO] 使用 mygene 转换 {len(ensembl_ids)} 个 Ensembl ID...")
        results = mg.querymany(ensembl_ids, scopes="ensembl.gene", fields="symbol", species="human", verbose=False)
        mapping = {}
        for r in results:
            if "symbol" in r:
                mapping[r["query"]] = r["symbol"]
        # 需要用原始 index（含版本号）映射
        new_index = []
        for idx in df.index:
            base = str(idx).split(".")[0]
            new_index.append(mapping.get(base, idx))
        df.index = new_index
        df = df[df.index.notna() & (df.index != "")]
        df = df.groupby(df.index).mean()
        print(f"[OK] 转换完成: {len(df)} 个基因")
        return df
    except ImportError:
        print("[WARN] mygene 未安装，跳过 Ensembl 转换。")
        return df
    except Exception as e:
        print(f"[ERROR] Ensembl 转换失败: {e}")
        return df


def harmonize_file(input_path, output_path=None):
    """统一单个文件的基因标识。"""
    print(f"\n{'='*60}")
    print(f"处理: {input_path.name}")
    print(f"{'='*60}")

    df = load_series_matrix(input_path)
    id_type = detect_id_type(df.index)
    print(f"原始基因标识类型: {id_type}")
    print(f"基因数: {len(df)}")

    if id_type == "gene_symbol":
        print("[INFO] 已经是 Gene Symbol，无需转换。")
        return df

    if id_type == "affymetrix_probe":
        df = harmonize_affymetrix(df)
    elif id_type == "entrez_id":
        df = harmonize_entrez(df)
    elif id_type == "ensembl_id":
        df = harmonize_ensembl(df)

    if output_path:
        df.to_csv(output_path, sep="\t")
        print(f"[OK] 已保存: {output_path}")

    return df


def main():
    parser = argparse.ArgumentParser(description="统一基因标识")
    parser.add_argument("--input", help="输入文件路径")
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--all", action="store_true", help="处理所有已下载的数据集")
    args = parser.parse_args()

    if not args.input and not args.all:
        print("[ERROR] 请指定 --input 或 --all")
        return 1

    if args.all:
        matrix_files = list(PROCESSED_DIR.glob("*_series_matrix.txt.gz"))
        print(f"[INFO] 找到 {len(matrix_files)} 个文件")
        for f in sorted(matrix_files):
            output = PROCESSED_DIR / f"{f.stem.replace('.txt', '')}_genesymbol.tsv"
            harmonize_file(f, output)
    else:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"[ERROR] 文件不存在: {input_path}")
            return 1
        output = Path(args.output) if args.output else None
        harmonize_file(input_path, output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
