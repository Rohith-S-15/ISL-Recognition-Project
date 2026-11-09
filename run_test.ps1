
# Start the Flask app and let it run for 20 seconds, capturing output
$proc = Start-Process python -ArgumentList "run_dashboard.py" -WorkingDirectory "C:\Projects\New Approach\ISL_Similarity_App" -NoNewWindow -RedirectStandardOutput "output.log" -RedirectStandardError "error.log" -PassThru

# Wait 20 seconds
Write-Host "[WAIT] Waiting 20 seconds for app to initialize..."
Start-Sleep -Seconds 20

# Kill the process
Stop-Process -InputObject $proc -Force

# Read and display the logs
Write-Host "`n[OUTPUT] Last 50 lines of stdout:"
Get-Content "output.log" -Tail 50

Write-Host "`n[ERROR] Last 30 lines of stderr:"
Get-Content "error.log" -Tail 30

Write-Host "`n[STATUS] Process ended"
