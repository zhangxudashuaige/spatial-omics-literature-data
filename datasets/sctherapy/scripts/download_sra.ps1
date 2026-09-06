# download_sra.ps1
# 下载 scTherapy AML 患者 SRA 原始数据
#
# 默认只显示将要下载的文件和预计大小。
# 只有用户明确确认后才真正下载三个 SRA 数据。
#
# 用法:
#   powershell -File scripts/download_sra.ps1           # 仅显示
#   powershell -File scripts/download_sra.ps1 -Confirm   # 确认下载

param(
    [switch]$Confirm = $false
)

$ErrorActionPreference = "Stop"

# SRA accession 列表
$SRA_RUNS = @(
    @{ Run = "SRR30720408"; Patient = "Patient 5"; Cancer = "AML" },
    @{ Run = "SRR30720407"; Patient = "Patient 6"; Cancer = "AML" },
    @{ Run = "SRR30720406"; Patient = "Patient 12"; Cancer = "AML" }
)

$DataDir = Join-Path $PSScriptRoot "..\data\raw"
$SraDir = Join-Path $DataDir "sra"
$FastqDir = Join-Path $DataDir "fastq"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "scTherapy SRA 数据下载" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查工具
$hasPrefetch = Get-Command prefetch -ErrorAction SilentlyContinue
$hasFasterq = Get-Command fasterq-dump -ErrorAction SilentlyContinue

if (-not $hasPrefetch) {
    Write-Host "[WARN] prefetch 未找到。请安装 SRA Toolkit:" -ForegroundColor Yellow
    Write-Host "       https://github.com/ncbi/sra-tools" -ForegroundColor Yellow
}
if (-not $hasFasterq) {
    Write-Host "[WARN] fasterq-dump 未找到。" -ForegroundColor Yellow
}
Write-Host ""

# 显示将要下载的文件
Write-Host "将要下载的 SRA 数据:" -ForegroundColor White
Write-Host "----------------------------------------" -ForegroundColor Gray
$totalEstimatedSize = 0
foreach ($run in $SRA_RUNS) {
    # SRA 文件通常每个 run 几百 MB 到几 GB
    # 这里显示估计值，实际大小以 SRA 为准
    $estimatedGB = 2.0
    $totalEstimatedSize += $estimatedGB
    Write-Host "  Run:     $($run.Run)" -ForegroundColor White
    Write-Host "  Patient: $($run.Patient)" -ForegroundColor White
    Write-Host "  Cancer:  $($run.Cancer)" -ForegroundColor White
    Write-Host "  估计大小: ~$estimatedGB GB (SRA + FASTQ)" -ForegroundColor Gray
    Write-Host "  URL:     https://trace.ncbi.nlm.nih.gov/Traces/?view=run_browser&acc=$($run.Run)" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host "总计估计: ~$totalEstimatedSize GB" -ForegroundColor Yellow
Write-Host "输出目录: $DataDir" -ForegroundColor Gray
Write-Host ""

# 大文件警告
Write-Host "[WARN] 这是大型原始测序数据。" -ForegroundColor Yellow
Write-Host "[WARN] 下载的文件不会进入 Git (已被 .gitignore 排除)。" -ForegroundColor Yellow
Write-Host "[WARN] 请确保磁盘空间充足。" -ForegroundColor Yellow
Write-Host ""

if (-not $Confirm) {
    Write-Host "[INFO] 这是预览模式，未实际下载。" -ForegroundColor Green
    Write-Host "[INFO] 确认下载请运行:" -ForegroundColor Green
    Write-Host "       powershell -File scripts/download_sra.ps1 -Confirm" -ForegroundColor Green
    Write-Host ""
    Write-Host "[INFO] 或者手动使用 SRA Toolkit:" -ForegroundColor Green
    Write-Host "       prefetch SRR30720408 --output-directory data/raw/sra" -ForegroundColor Gray
    Write-Host "       fasterq-dump SRR30720408 --outdir data/raw/fastq --split-files" -ForegroundColor Gray
    exit 0
}

# 确认下载
Write-Host "[INFO] 开始下载..." -ForegroundColor Green
Write-Host ""

New-Item -ItemType Directory -Force -Path $SraDir | Out-Null
New-Item -ItemType Directory -Force -Path $FastqDir | Out-Null

foreach ($run in $SRA_RUNS) {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "下载 $($run.Run) ($($run.Patient))" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    # 1. prefetch 下载 SRA 文件
    if ($hasPrefetch) {
        Write-Host "[STEP 1] prefetch $($run.Run)..." -ForegroundColor White
        & prefetch $run.Run --output-directory $SraDir
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] prefetch 失败: $($run.Run)" -ForegroundColor Red
            continue
        }
        Write-Host "[OK] SRA 文件下载完成" -ForegroundColor Green
    } else {
        Write-Host "[SKIP] prefetch 不可用，跳过 SRA 下载" -ForegroundColor Yellow
    }

    # 2. fasterq-dump 转换为 FASTQ
    $sraFile = Join-Path $SraDir "$($run.Run).sra"
    if ($hasFasterq -and (Test-Path $sraFile)) {
        Write-Host "[STEP 2] fasterq-dump $($run.Run)..." -ForegroundColor White
        & fasterq-dump $run.Run --outdir $FastqDir --split-files --threads 4
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] fasterq-dump 失败: $($run.Run)" -ForegroundColor Red
            continue
        }
        Write-Host "[OK] FASTQ 转换完成" -ForegroundColor Green
    } else {
        Write-Host "[SKIP] fasterq-dump 不可用或 SRA 文件不存在" -ForegroundColor Yellow
    }

    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "下载完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SRA 文件: $SraDir" -ForegroundColor Gray
Write-Host "FASTQ 文件: $FastqDir" -ForegroundColor Gray
Write-Host ""
Write-Host "[INFO] 下一步: 使用 CellRanger/STARsolo 等工具进行比对和定量" -ForegroundColor Green
