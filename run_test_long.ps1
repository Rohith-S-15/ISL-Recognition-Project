
# Start the Flask app and let it run for 60 seconds, capturing output
$proc = Start-Process python -ArgumentList "run_dashboard.py" -WorkingDirectory "C:\Projects\New Approach\ISL_Similarity_App" -NoNewWindow -RedirectStandardOutput "output.log" -RedirectStandardError "error.log" -PassThru

# Wait 60 seconds
Write-Host "[WAIT] Waiting 60 seconds for app to fully initialize..."
Start-Sleep -Seconds 60

# Kill the process
Stop-Process -InputObject $proc -Force

# Read and display the logs
Write-Host "`n[OUTPUT] FULL stdout log:"
Get-Content "output.log"

Write-Host "`n[STATUS] Process ended"
