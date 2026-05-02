$LogDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogFile = Join-Path $LogDir "kimi-token-refresh.log"
$TimeStamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

"[$TimeStamp] Starting Kimi token refresh..." | Out-File -FilePath $LogFile -Append -Encoding UTF8

$result = wsl -d Ubuntu-24.04 -e python3 /home/yaya/refresh-kimi-token.py 2>&1
$result | Out-File -FilePath $LogFile -Append -Encoding UTF8

$TimeStamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
"[$TimeStamp] Exit code: $LASTEXITCODE" | Out-File -FilePath $LogFile -Append -Encoding UTF8
"" | Out-File -FilePath $LogFile -Append -Encoding UTF8
