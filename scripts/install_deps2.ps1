$nodeBin = "$env:LOCALAPPDATA\node"
$env:PATH = "$nodeBin;$env:PATH"
$frontendPath = "C:\Users\Pierre-PhilippeCrépi\OneDrive - EIFFEL IG\Desktop\PythonProjects\Agora\frontend"
Set-Location $frontendPath
Write-Host "CWD: $(Get-Location)"
Write-Host "Installing zustand + plotly..."
& "$nodeBin\npm.cmd" install zustand plotly.js react-plotly.js @types/react-plotly.js
Write-Host "Exit: $LASTEXITCODE"
Write-Host "Zustand exists: $(Test-Path 'node_modules\zustand')"
Write-Host "Plotly exists: $(Test-Path 'node_modules\plotly.js')"
