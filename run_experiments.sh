#!/usr/bin/env bash
# GhostInTheMachine: End-to-End Benchmark Execution Harness
set -e

echo "=========================================================================="
echo "Starting GhostInTheMachine Execution Engine & Telemetry Pipeline"
echo "=========================================================================="

# Run full scenario matrix across seeds and churn configurations
python run_experiments.py --tasks 20

echo "=========================================================================="
echo "Artifact Generation Complete! Check the 'artifacts/' directory."
echo "=========================================================================="
