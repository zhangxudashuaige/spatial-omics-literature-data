#!/usr/bin/env python3
"""检查图像数据：形状、类型、轴含义、通道、时间间隔。"""
import sys, argparse
from pathlib import Path
import numpy as np

BASE = Path(__file__).resolve().parent.parent

def inspect_tiff(filepath):
    try:
        from tifffile import TiffFile
    except ImportError:
        print("[ERROR] tifffile 未安装: pip install tifffile")
        return
    with TiffFile(filepath) as tif:
        print(f"页数: {len(tif.pages)}")
        for i, page in enumerate(tif.pages[:5]):
            print(f"  Page {i}: shape={page.shape}, dtype={page.dtype}")
        if hasattr(tif, "imagej_metadata") and tif.imagej_metadata:
            print(f"ImageJ元数据: {dict(tif.imagej_metadata)}")
        # 读取第一页
        arr = tif.pages[0].asarray()
        print(f"第一页形状: {arr.shape}, dtype: {arr.dtype}")
        print(f"值范围: [{arr.min()}, {arr.max()}]")

def inspect_nd2(filepath):
    try:
        from nd2 import ND2File
    except ImportError:
        print("[ERROR] nd2 未安装: pip install nd2")
        return
    with ND2File(filepath) as f:
        print(f"形状: {f.shape}")
        print(f"轴顺序: {f.axes}")
        print(f"dtype: {f.dtype}")
        meta = f.metadata
        print(f"通道数: {len(meta.channels) if hasattr(meta, 'channels') else 'N/A'}")
        if hasattr(meta, "channels"):
            for ch in meta.channels:
                print(f"  通道: {ch.channel.name if hasattr(ch, 'channel') else ch}")
        print(f"像素尺寸: {meta.voxel_size if hasattr(meta, 'voxel_size') else 'N/A'}")

def inspect_numpy(filepath):
    arr = np.load(filepath, mmap_mode="r")
    print(f"形状: {arr.shape}")
    print(f"dtype: {arr.dtype}")
    print(f"轴含义: 需手动确认（常见: TZYXC, TCZYX, TYXC）")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", required=True)
    args = p.parse_args()
    f = Path(args.file)
    if not f.exists():
        print(f"[ERROR] 文件不存在: {f}")
        return 1
    print(f"文件: {f.name} ({f.stat().st_size / 1024 / 1024:.1f} MB)")
    suffix = f.suffix.lower()
    if suffix in [".tif", ".tiff"]:
        inspect_tiff(f)
    elif suffix == ".nd2":
        inspect_nd2(f)
    elif suffix in [".npy", ".npz"]:
        inspect_numpy(f)
    else:
        print(f"[WARN] 不支持的格式: {suffix}")
        print("[INFO] 支持: .tif, .tiff, .nd2, .npy, .npz")
    return 0

if __name__ == "__main__":
    sys.exit(main())
