$localApp = $env:LOCALAPPDATA
$src = "$localApp\node-v22.15.0-win-x64"
$dst = "$localApp\node"

# Rename folder if needed
if (Test-Path $src) {
    if (Test-Path $dst) { Remove-Item $dst -Recurse -Force }
    Rename-Item $src $dst
    Write-Host "Renamed to: $dst"
}

# Verify
$nodePath = "$dst\node.exe"
if (Test-Path $nodePath) {
    Write-Host "node.exe OK"
    & $nodePath --version
    $npmPath = "$dst\npm.cmd"
    if (Test-Path $npmPath) {
        Write-Host "npm OK"
        & $npmPath --version
    }
} else {
    Write-Host "ERROR: node.exe not found"
}
