#!/usr/bin/env python3
"""生成并可选运行spatialLIBD官方R下载脚本。"""
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
R_CODE = '''
if (!requireNamespace("BiocManager", quietly = TRUE)) install.packages("BiocManager")
if (!requireNamespace("spatialLIBD", quietly = TRUE)) BiocManager::install("spatialLIBD", ask = FALSE)
spe <- spatialLIBD::fetch_data(type = "spe")
dir.create("datasets/dlpfc_visium/raw", recursive = TRUE, showWarnings = FALSE)
saveRDS(spe, "datasets/dlpfc_visium/raw/spatialLIBD_spe.rds")
print(spe)
sessionInfo()
'''.strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true", help="实际调用本机Rscript；默认只写脚本")
    args = parser.parse_args()
    target = ROOT / "datasets" / "dlpfc_visium" / "download_spatiallibd.local.R"
    target.write_text(R_CODE, encoding="utf-8")
    print(f"已写入 {target}")
    if args.run:
        rscript = shutil.which("Rscript")
        if not rscript:
            raise SystemExit("未找到Rscript；请先安装R和Bioconductor")
        subprocess.run([rscript, str(target)], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
