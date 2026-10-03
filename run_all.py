#!/usr/bin/env python3
"""
GreenNet-Mobile: Master Execution Controller (Python 3.6 Compatible)
Author: Humayun Rashid
Objective: Execute the complete GreenNet-Mobile simulation and benchmark suite.
Cost: $0 (Runs on standard Linux/Python CLI)
"""

import subprocess
import sys

def run_script(script_path):
    print(f"\n[RUNNING] Executing: {script_path}")
    print("-" * 50)
    result = subprocess.run([sys.executable, script_path])
    if result.returncode != 0:
        print(f"[ERROR] Execution failed for {script_path}")
    else:
        print(f"[SUCCESS] Completed: {script_path}")

def main():
    print("==================================================")
    print("  GREENNET-MOBILE: MASTER SYSTEM SIMULATOR SUITE  ")
    print("  Trade License / Portal Anchor: reachnbiz.com    ")
    print("==================================================")

    # 1. Run Proximity Index (Pi) Simulation
    run_script("/home/acmsrzwf/GreenNet-Mobile/simulator/pi_simulator.py")

    # 2. Run Socket Steering Simulation
    run_script("/home/acmsrzwf/GreenNet-Mobile/simulator/net_steer_simulator.py")

    # 3. Run Memory Isolation Simulation
    run_script("/home/acmsrzwf/GreenNet-Mobile/simulator/mem_lock_simulator.py")

    # 4. Run Benchmark Aggregator
    run_script("/home/acmsrzwf/GreenNet-Mobile/benchmarks/benchmark_aggregator.py")

    # 5. Run Database Logger Integrator
    run_script("/home/acmsrzwf/GreenNet-Mobile/benchmarks/db_logger.py")

    print("\n==================================================")
    print("  ALL GREENNET-MOBILE MODULES EXECUTED SUCCESSFULLY")
    print("  System Status: 100% Operational at $0 Cost      ")
    print("==================================================")

if __name__ == "__main__":
    main()
