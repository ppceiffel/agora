$nodeBin = "$env:LOCALAPPDATA\node"
$env:PATH = "$nodeBin;$env:PATH"
$projectRoot = "C:\Users\Pierre-PhilippeCrépi\OneDrive - EIFFEL IG\Desktop\PythonProjects\Agora"
Set-Location $projectRoot

Write-Host "Node: $(& "$nodeBin\node.exe" --version)"
Write-Host "npm: $(& "$nodeBin\npm.cmd" --version)"
Write-Host "Creating Next.js frontend..."

$npx = "$nodeBin\npx.cmd"
& $npx create-next-app@latest frontend --typescript --tailwind --app --no-git --no-eslint --import-alias "@/*" --yes 2>&1
Write-Host "Exit code: $LASTEXITCODE"
