$url = "https://aka.ms/vs/17/release/vs_buildtools.exe"
$output = "$env:TEMP\vs_buildtools.exe"
Write-Host "Downloading Visual Studio Build Tools..."
Invoke-WebRequest -Uri $url -OutFile $output
Write-Host "Installing Visual Studio Build Tools (This will take 5-15 minutes)..."
$argsList = @("--quiet", "--wait", "--norestart", "--nocache", "--add", "Microsoft.VisualStudio.Workload.VCTools", "--includeRecommended")
Start-Process -FilePath $output -ArgumentList $argsList -Wait -NoNewWindow
Write-Host "Installation completed!"
