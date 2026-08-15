param(
    [Parameter(Mandatory = $true)]
    [string]$Path
)

$resolved = Resolve-Path -LiteralPath $Path -ErrorAction Stop
Get-FileHash -LiteralPath $resolved -Algorithm SHA256 |
    Select-Object Path, Algorithm, Hash

