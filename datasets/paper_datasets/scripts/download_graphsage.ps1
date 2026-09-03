[CmdletBinding()]
param(
    [ValidateSet('PPI', 'Reddit', 'All')]
    [string]$Dataset = 'All',
    [string]$OutputDirectory,
    [switch]$Force,
    [switch]$AllowHttpFallback
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
if (-not $OutputDirectory) {
    $OutputDirectory = Join-Path $ProjectRoot 'data\graphsage\raw'
}
$OutputDirectory = [System.IO.Path]::GetFullPath($OutputDirectory)
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null

$Sources = @(
    [pscustomobject]@{
        Name = 'PPI'
        FileName = 'ppi.zip'
        HttpsUrl = 'https://snap.stanford.edu/graphsage/ppi.zip'
        HttpUrl = 'http://snap.stanford.edu/graphsage/ppi.zip'
        ExpectedBytes = 27029260
    },
    [pscustomobject]@{
        Name = 'Reddit'
        FileName = 'reddit.zip'
        HttpsUrl = 'https://snap.stanford.edu/graphsage/reddit.zip'
        HttpUrl = 'http://snap.stanford.edu/graphsage/reddit.zip'
        ExpectedBytes = 1308432264
    }
)

if ($Dataset -ne 'All') {
    $Sources = $Sources | Where-Object Name -eq $Dataset
}

function Invoke-CurlDownload {
    param([string]$Url, [string]$Destination)
    $arguments = @(
        '--location', '--fail', '--show-error',
        '--retry', '8', '--retry-delay', '3', '--retry-all-errors',
        '--connect-timeout', '60',
        '--continue-at', '-', '--output', $Destination, $Url
    )
    & curl.exe @arguments
    return $LASTEXITCODE
}

foreach ($Source in $Sources) {
    $Destination = Join-Path $OutputDirectory $Source.FileName
    $PartPath = "$Destination.part"
    if ($Force) {
        if (Test-Path -LiteralPath $Destination) { Remove-Item -LiteralPath $Destination -Force }
        if (Test-Path -LiteralPath $PartPath) { Remove-Item -LiteralPath $PartPath -Force }
    }
    if ((Test-Path -LiteralPath $Destination) -and (Get-Item -LiteralPath $Destination).Length -ne $Source.ExpectedBytes) {
        if (Test-Path -LiteralPath $PartPath) {
            throw "同时发现不完整目标文件和 .part 文件，请人工确认后保留较大的一个：$Destination"
        }
        Move-Item -LiteralPath $Destination -Destination $PartPath
    }

    $TransferUrl = $Source.HttpsUrl
    if (-not (Test-Path -LiteralPath $Destination)) {
        Write-Host "下载 $($Source.Name): $TransferUrl"
        $exitCode = Invoke-CurlDownload -Url $TransferUrl -Destination $PartPath
        if ($exitCode -ne 0 -and $AllowHttpFallback) {
            $TransferUrl = $Source.HttpUrl
            Write-Warning "HTTPS 下载失败；按显式授权回退到同一官方主机的 HTTP：$TransferUrl"
            $exitCode = Invoke-CurlDownload -Url $TransferUrl -Destination $PartPath
        }
        if ($exitCode -ne 0) {
            throw "下载失败（curl exit $exitCode）：$($Source.HttpsUrl)。如属 SNAP TLS 握手问题，可加 -AllowHttpFallback。"
        }
        $PartFile = Get-Item -LiteralPath $PartPath
        if ($PartFile.Length -ne $Source.ExpectedBytes) {
            throw "文件大小不符：$PartPath，实际 $($PartFile.Length)，官方请求头记录 $($Source.ExpectedBytes)。"
        }
        Move-Item -LiteralPath $PartPath -Destination $Destination
    }

    $File = Get-Item -LiteralPath $Destination
    if ($File.Length -ne $Source.ExpectedBytes) {
        throw "文件大小不符：$Destination，实际 $($File.Length)，官方请求头记录 $($Source.ExpectedBytes)。"
    }
    $Hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Destination).Hash.ToLowerInvariant()
    $Record = [ordered]@{
        dataset = $Source.Name
        source_url = $Source.HttpsUrl
        transfer_url = $TransferUrl
        downloaded_at_utc = (Get-Date).ToUniversalTime().ToString('o')
        file_name = $Source.FileName
        local_path = $Destination
        size_bytes = $File.Length
        sha256 = $Hash
        license_or_use_restrictions = 'GraphSAGE 项目页未声明该预处理数据包的独立许可证；使用前核查原始数据源条款。'
    }
    $RecordPath = "$Destination.download.json"
    $Record | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $RecordPath -Encoding utf8
    Write-Host "完成：$Destination"
    Write-Host "SHA256：$Hash"
    Write-Host "本地记录：$RecordPath"
}
