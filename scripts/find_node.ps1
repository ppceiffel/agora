$localApp = $env:LOCALAPPDATA
Write-Host "LOCALAPPDATA: $localApp"
$items = Get-ChildItem $localApp | Where-Object { $_.Name -like "node*" }
foreach ($item in $items) {
    Write-Host "Found: $($item.FullName)"
}
$nodePath = "$localApp\node\node.exe"
if (Test-Path $nodePath) {
    Write-Host "Node found at: $nodePath"
    & $nodePath --version
} else {
    Write-Host "node.exe NOT found at $nodePath"
}
