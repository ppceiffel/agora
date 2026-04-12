$nodeBin = "$env:LOCALAPPDATA\node"
$env:PATH = "$nodeBin;$env:PATH"
$frontendPath = "C:\Users\Pierre-PhilippeCrépi\OneDrive - EIFFEL IG\Desktop\PythonProjects\Agora\frontend"

Write-Host "Installing additional dependencies..."
& "$nodeBin\npm.cmd" --prefix $frontendPath install zustand plotly.js react-plotly.js
Write-Host "Installing type definitions..."
& "$nodeBin\npm.cmd" --prefix $frontendPath install --save-dev @types/react-plotly.js
Write-Host "Done. Exit: $LASTEXITCODE"
