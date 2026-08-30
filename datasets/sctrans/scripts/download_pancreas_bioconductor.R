#!/usr/bin/env Rscript
# 下载四套标准化 Bioconductor SingleCellExperiment，并记录真实软件版本。
if (!requireNamespace("BiocManager", quietly = TRUE)) stop("Install BiocManager first")
if (!requireNamespace("scRNAseq", quietly = TRUE)) BiocManager::install("scRNAseq", ask = FALSE)

all_args <- commandArgs(trailingOnly = FALSE)
script_arg <- grep("^--file=", all_args, value = TRUE)
if (length(script_arg) != 1) stop("Cannot determine script path")
script_path <- normalizePath(sub("^--file=", "", script_arg), mustWork = TRUE)
root <- dirname(dirname(script_path))
raw_root <- file.path(root, "raw", "pancreas")
dir.create(raw_root, recursive = TRUE, showWarnings = FALSE)

objects <- list(
  baron = scRNAseq::BaronPancreasData("human"),
  xin = scRNAseq::XinPancreasData(),
  segerstolpe = scRNAseq::SegerstolpePancreasData(),
  muraro = scRNAseq::MuraroPancreasData()
)
for (name in names(objects)) {
  dir.create(file.path(raw_root, name), recursive = TRUE, showWarnings = FALSE)
  saveRDS(objects[[name]], file.path(raw_root, name, paste0(name, "_scRNAseq.rds")))
}
info <- list(
  downloaded_at = format(Sys.time(), tz = "UTC", usetz = TRUE),
  R = R.version.string,
  Bioconductor = as.character(BiocManager::version()),
  scRNAseq = as.character(packageVersion("scRNAseq")),
  datasets = lapply(objects, function(x) list(dim = dim(x), assays = assayNames(x), colData = colnames(colData(x)), rowData = colnames(rowData(x))))
)
if (!requireNamespace("jsonlite", quietly = TRUE)) install.packages("jsonlite", repos = "https://cloud.r-project.org")
jsonlite::write_json(info, file.path(raw_root, "bioconductor_versions.local.json"), auto_unbox = TRUE, pretty = TRUE)
