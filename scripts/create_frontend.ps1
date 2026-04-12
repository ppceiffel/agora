$nodeBin = "$env:LOCALAPPDATA\node"
$env:PATH = "$nodeBin;$env:PATH"
$projectRoot = "c:\Users\Pierre-PhilippeCr`u00e9pi\OneDrive - EIFFEL IG\Desktop\PythonProjects\Agora"

Set-Location $projectRoot

Write-Host "Creating Next.js app..."
& "$nodeBin\npx.cmd" create-next-app@latest frontend `
    --typescript `
    --tailwind `
    --app `
    --no-git `
    --no-eslint `
    --import-alias "@/*" `
    --yes

Write-Host "Done."
