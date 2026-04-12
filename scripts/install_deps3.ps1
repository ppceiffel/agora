$nodeBin = "$env:LOCALAPPDATA\node"
$env:PATH = "$nodeBin;$env:PATH"

# Find the frontend directory
$base = Split-Path -Parent $PSScriptRoot
$frontendPath = Join-Path $base "frontend"

Write-Host "Frontend path: $frontendPath"
Write-Host "Exists: $(Test-Path $frontendPath)"
Set-Location $frontendPath

Write-Host "Installing dependencies..."
& "$nodeBin\npm.cmd" install zustand plotly.js react-plotly.js @types/react-plotly.js
Write-Host "Exit: $LASTEXITCODE"
Write-Host "Zustand: $(Test-Path 'node_modules\zustand')"
Write-Host "Plotly: $(Test-Path 'node_modules\plotly.js')"
