#!/usr/bin/env Rscript
# download_vespucci_demo.R
# 下载 Vespucci 模拟数据（小型可运行示例）
#
# 数据来源: https://github.com/neurorestore/Vespucci
# 包含: spatial_sim, spatial_sim_distance_metrics_df
#
# 用法:
#   Rscript download_vespucci_demo.R

# 设置输出目录
base_dir <- dirname(dirname(normalizePath(sys.frame(1)$ofile)))
if (is.null(base_dir)) {
  base_dir <- getwd()
}
sim_dir <- file.path(base_dir, "data", "simulated")
dir.create(sim_dir, recursive = TRUE, showWarnings = FALSE)

cat("========================================\n")
cat("Vespucci 模拟数据下载\n")
cat("========================================\n")
cat(sprintf("输出目录: %s\n", sim_dir))
cat("\n")

# 方法1: 从 GitHub 仓库下载 RDA/RDS 文件
# Vespucci 仓库中的数据文件
github_base <- "https://raw.githubusercontent.com/neurorestore/Vespucci/main"

# 尝试下载的数据文件
data_files <- c(
  "data/spatial_sim.rda",
  "data/spatial_sim_distance_metrics_df.rda",
  "data/spatial_sim.RData",
  "data/spatial_sim_distance_metrics_df.RData",
  "inst/extdata/spatial_sim.rda",
  "inst/extdata/spatial_sim_distance_metrics_df.rda"
)

downloaded <- c()

for (f in data_files) {
  url <- file.path(github_base, f)
  dest <- file.path(sim_dir, basename(f))

  if (file.exists(dest)) {
    cat(sprintf("[SKIP] 已存在: %s\n", basename(f)))
    downloaded <- c(downloaded, basename(f))
    next
  }

  cat(sprintf("[INFO] 尝试下载: %s\n", url))
  tryCatch({
    download.file(url, dest, quiet = FALSE, mode = "wb")
    size <- file.info(dest)$size
    cat(sprintf("[OK] 下载完成: %s (%.1f KB)\n", basename(f), size / 1024))
    downloaded <- c(downloaded, basename(f))
  }, error = function(e) {
    cat(sprintf("[WARN] 下载失败: %s\n", e$message))
    if (file.exists(dest)) file.remove(dest)
  })
}

# 方法2: 如果 GitHub 下载失败，尝试安装 Vespucci 包并加载数据
if (length(downloaded) == 0) {
  cat("\n")
  cat("[INFO] GitHub 直接下载未成功，尝试安装 Vespucci 包...\n")

  if (!requireNamespace("remotes", quietly = TRUE)) {
    cat("[INFO] 安装 remotes 包...\n")
    install.packages("remotes", repos = "https://cloud.r-project.org")
  }

  tryCatch({
    remotes::install_github("neurorestore/Vespucci", quiet = FALSE)
    library(Vespucci)

    # 加载数据
    if (exists("spatial_sim")) {
      save(spatial_sim, file = file.path(sim_dir, "spatial_sim.rda"))
      cat("[OK] spatial_sim 已保存\n")
      downloaded <- c(downloaded, "spatial_sim.rda")
    }
    if (exists("spatial_sim_distance_metrics_df")) {
      save(spatial_sim_distance_metrics_df,
           file = file.path(sim_dir, "spatial_sim_distance_metrics_df.rda"))
      cat("[OK] spatial_sim_distance_metrics_df 已保存\n")
      downloaded <- c(downloaded, "spatial_sim_distance_metrics_df.rda")
    }
  }, error = function(e) {
    cat(sprintf("[ERROR] 安装/加载失败: %s\n", e$message))
  })
}

# 验证下载的数据
cat("\n")
cat("========================================\n")
cat("数据验证\n")
cat("========================================\n")

for (f in list.files(sim_dir, pattern = "\\.(rda|RData)$", full.names = TRUE)) {
  cat(sprintf("\n文件: %s\n", basename(f)))
  tryCatch({
    env <- new.env()
    load(f, envir = env)
    obj_names <- ls(env)
    cat(sprintf("  对象: %s\n", paste(obj_names, collapse = ", ")))
    for (obj in obj_names) {
      data_obj <- get(obj, envir = env)
      if (is.data.frame(data_obj)) {
        cat(sprintf("  %s: data.frame %d x %d\n", obj, nrow(data_obj), ncol(data_obj)))
        cat(sprintf("    列: %s\n", paste(colnames(data_obj), collapse = ", ")))
      } else if (is.matrix(data_obj)) {
        cat(sprintf("  %s: matrix %d x %d\n", obj, nrow(data_obj), ncol(data_obj)))
      } else if (is.list(data_obj)) {
        cat(sprintf("  %s: list with %d elements\n", obj, length(data_obj)))
      } else {
        cat(sprintf("  %s: %s\n", obj, class(data_obj)[1]))
      }
    }
  }, error = function(e) {
    cat(sprintf("  [ERROR] 加载失败: %s\n", e$message))
  })
}

cat("\n")
cat("========================================\n")
cat("完成\n")
cat("========================================\n")
cat(sprintf("下载文件数: %d\n", length(downloaded)))
cat(sprintf("输出目录: %s\n", sim_dir))
cat("\n")

if (length(downloaded) == 0) {
  cat("[WARN] 未能自动下载模拟数据。\n")
  cat("[WARN] 请手动访问: https://github.com/neurorestore/Vespucci\n")
  cat("[WARN] 查找 data/ 目录中的 spatial_sim 文件，手动下载到 data/simulated/\n")
  quit(status = 1)
}

cat("[OK] Vespucci 模拟数据下载完成，可作为项目可运行示例。\n")
