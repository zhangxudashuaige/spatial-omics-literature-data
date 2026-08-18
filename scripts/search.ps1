param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Query
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$searchTargets = @(
    (Join-Path $repoRoot "catalog"),
    (Join-Path $repoRoot "papers")
)

$ripgrep = Get-Command rg -ErrorAction SilentlyContinue
if ($null -ne $ripgrep) {
    & $ripgrep.Source --line-number --color never --fixed-strings $Query @searchTargets
    exit $LASTEXITCODE
}

Write-Host "rg was not found; using PowerShell Select-String." -ForegroundColor Yellow
$files = Get-ChildItem -LiteralPath $searchTargets -Recurse -File
$matches = $files | Select-String -SimpleMatch -Pattern $Query
$matches | ForEach-Object {
    $relative = [System.IO.Path]::GetRelativePath($repoRoot, $_.Path)
    "{0}:{1}:{2}" -f $relative, $_.LineNumber, $_.Line.Trim()
}

if ($matches.Count -eq 0) {
    exit 1
}
