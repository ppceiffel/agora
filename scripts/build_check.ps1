$nodeBin = "$env:LOCALAPPDATA\node"
$env:PATH = "$nodeBin;$env:PATH"
$base = Split-Path -Parent $PSScriptRoot
$frontendPath = Join-Path $base "frontend"
Set-Location $frontendPath

Write-Host "Checking deps..."
Write-Host "zustand: $(Test-Path 'node_modules\zustand')"
Write-Host "plotly.js: $(Test-Path 'node_modules\plotly.js')"
Write-Host "react-plotly.js: $(Test-Path 'node_modules\react-plotly.js')"

if (-not (Test-Path 'node_modules\zustand')) {
    Write-Host "Installing missing deps..."
    & "$nodeBin\npm.cmd" install zustand plotly.js react-plotly.js @types/react-plotly.js
}

Write-Host "Running TypeScript check..."
& "$nodeBin\npx.cmd" tsc --noEmit 2>&1
Write-Host "TSC exit: $LASTEXITCODE"
