# GhostInTheMachine: End-to-End Benchmark Execution Harness (PowerShell)
$ErrorActionPreference = "Stop"

Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host "Starting GhostInTheMachine Execution Engine & Telemetry Pipeline" -ForegroundColor Green
Write-Host "==========================================================================" -ForegroundColor Cyan

python run_experiments.py --tasks 20

Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host "Artifact Generation Complete! Check the 'artifacts/' directory." -ForegroundColor Green
Write-Host "==========================================================================" -ForegroundColor Cyan
