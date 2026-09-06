#!/usr/bin/env Rscript
# inspect_seurat.R
# 检查 scTherapy 处理后的 Seurat 对象。
#
# 展示:
# - Seurat 对象大小
# - 细胞数和基因数
# - metadata 列
# - 患者分布
# - 细胞类型分布
# - 正常/恶性细胞标签
# - 稀疏表达矩阵前几行
# - UMAP 图 (如果对象包含 UMAP)
#
# 用法:
#   Rscript scripts/inspect_seurat.R data/processed/<object>.rds

args <- commandArgs(trailingOnly = TRUE)

if (length(args) == 0) {
  cat("用法: Rscript inspect_seurat.R <seurat_object.rds>\n")
  quit(status = 1)
}

input_path <- args[1]

if (!file.exists(input_path)) {
  cat(sprintf("[ERROR] 文件不存在: %s\n", input_path))
  quit(status = 1)
}

cat("================================================================\n")
cat(sprintf("Seurat 对象检查: %s\n", basename(input_path)))\n")
cat("================================================================\n")
cat(sprintf("文件路径: %s\n", normalizePath(input_path)))\n")

# 文件大小
file_size <- file.info(input_path)$size
cat(sprintf("文件大小: %.2f MB\n", file_size / (1024^2)))\n")
cat("\n")

# 加载 Seurat
suppressPackageStartupMessages({
  has_seurat <- requireNamespace("Seurat", quietly = TRUE)
})

if (!has_seurat) {
  cat("[ERROR] Seurat 未安装。请运行: install.packages('Seurat')\n")
  quit(status = 1)
}

library(Seurat)

cat("[INFO] 加载 Seurat 对象...\n")
obj <- readRDS(input_path)
cat("\n")

# 对象基本信息
cat("----------------------------------------------------------------\n")
cat("基本信息\n")
cat("----------------------------------------------------------------\n")
cat(sprintf("对象类: %s\n", class(obj)[1]))\n")
cat(sprintf("细胞数: %d\n", ncol(obj)))\n")
cat(sprintf("基因数: %d\n", nrow(obj)))\n")
cat(sprintf("Assays: %s\n", paste(names(obj@assays), collapse = ", ")))\n")
cat(sprintf("Reductions: %s\n", paste(names(obj@reductions), collapse = ", ")))\n")
cat("\n")

# metadata
cat("----------------------------------------------------------------\n")
cat("Metadata 列\n")
cat("----------------------------------------------------------------\n")
meta <- obj@meta.data
cat(sprintf("列数: %d\n", ncol(meta)))\n")
for (col in colnames(meta)) {
  cat(sprintf("  - %s: %s (unique: %d)\n",
              col, class(meta[[col]])[1], length(unique(meta[[col]]))))
  if (length(unique(meta[[col]])) <= 20) {
    counts <- sort(table(meta[[col]]), decreasing = TRUE)
    cat(sprintf("    值: %s\n",
                paste(sprintf("%s=%d", names(counts), counts), collapse = ", "))))
  }
}
cat("\n")

# 患者分布
patient_col <- NULL
for (col in c("patient", "Patient", "patient_id", "sample", "donor")) {
  if (col %in% colnames(meta)) {
    patient_col <- col
    break
  }
}

if (!is.null(patient_col)) {
  cat("----------------------------------------------------------------\n")
  cat(sprintf("患者分布 (%s)\n", patient_col))\n")
  cat("----------------------------------------------------------------\n")
  patient_counts <- sort(table(meta[[patient_col]]), decreasing = TRUE)
  print(patient_counts)
  cat("\n")
}

# 细胞类型分布
celltype_col <- NULL
for (col in c("cell_type", "CellType", "celltype", "cluster", "seurat_clusters")) {
  if (col %in% colnames(meta)) {
    celltype_col <- col
    break
  }
}

if (!is.null(celltype_col)) {
  cat("----------------------------------------------------------------\n")
  cat(sprintf("细胞类型分布 (%s)\n", celltype_col))\n")
  cat("----------------------------------------------------------------\n")
  ct_counts <- sort(table(meta[[celltype_col]]), decreasing = TRUE)
  print(ct_counts)
  cat("\n")
}

# 正常/恶性细胞标签
malignant_col <- NULL
for (col in c("malignant", "Malignant", "is_malignant", "cell_status", "malignancy")) {
  if (col %in% colnames(meta)) {
    malignant_col <- col
    break
  }
}

if (!is.null(malignant_col)) {
  cat("----------------------------------------------------------------\n")
  cat(sprintf("正常/恶性细胞标签 (%s)\n", malignant_col))\n")
  cat("----------------------------------------------------------------\n")
  print(table(meta[[malignant_col]]))
  cat("\n")
}

# 表达矩阵
cat("----------------------------------------------------------------\n")
cat("表达矩阵\n")
cat("----------------------------------------------------------------\n")
default_assay <- DefaultAssay(obj)
cat(sprintf("默认 Assay: %s\n", default_assay))\n")

expr <- GetAssayData(obj, assay = default_assay, slot = "counts")
cat(sprintf("counts 矩阵: %d x %d\n", nrow(expr), ncol(expr)))\n")
cat(sprintf("稀疏矩阵: %s\n", is(expr, "sparseMatrix")))\n")
if (is(expr, "sparseMatrix")) {
  cat(sprintf("非零元素: %d (%.2f%%)\n",
              length(expr@x),
              100 * length(expr@x) / (nrow(expr) * ncol(expr))))
}
cat("\n")

cat("前 5 个基因 x 前 5 个细胞的计数:\n")
top_left <- expr[1:min(5, nrow(expr)), 1:min(5, ncol(expr))]
if (is(top_left, "sparseMatrix")) {
  print(as.matrix(top_left))
} else {
  print(top_left)
}
cat("\n")

# UMAP
if ("umap" %in% names(obj@reductions)) {
  cat("----------------------------------------------------------------\n")
  cat("UMAP\n")
  cat("----------------------------------------------------------------\n")
  umap <- Embeddings(obj, reduction = "umap")
  cat(sprintf("UMAP 维度: %d x %d\n", nrow(umap), ncol(umap)))\n")
  cat(sprintf("前 5 个细胞 UMAP 坐标:\n"))\n")
  print(head(umap, 5))
  cat("\n")

  # 尝试绘制 UMAP
  has_ggplot <- requireNamespace("ggplot2", quietly = TRUE)
  if (has_ggplot) {
    output_dir <- dirname(input_path)
    umap_file <- file.path(output_dir, "umap_inspection.png")
    cat(sprintf("[INFO] 绘制 UMAP 图: %s\n", umap_file))\n")
    tryCatch({
      p <- DimPlot(obj, reduction = "umap",
                   group.by = if (!is.null(celltype_col)) celltype_col else NULL)
      ggplot2::ggsave(umap_file, p, width = 8, height = 6, dpi = 150)
      cat("[OK] UMAP 图已保存\n")
    }, error = function(e) {
      cat(sprintf("[WARN] UMAP 绘制失败: %s\n", e$message))\n")
    })
  }
  cat("\n")
} else {
  cat("[INFO] 对象不包含 UMAP reduction。\n")
  cat("\n")
}

cat("================================================================\n")
cat("检查完成\n")
cat("================================================================\n")
