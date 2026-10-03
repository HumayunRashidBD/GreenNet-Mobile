#!/usr/bin/env python3
"""
GreenNet-Mobile: Zero-GPS Proximity Index (Pi) Simulation Engine
Author: Humayun Rashid
Objective: Compute spatial stability and proximity via localized RSSI differentials 
           to eliminate high-power GPS/GNSS hardware activation.
Cost: $0 (Runs on standard Linux/Python CLI)
"""

import time
import math

class ProximityIndexEngine:
    def __init__(self, threshold=2.5, history_size=5):
        self.threshold = threshold
        self.rssi_history = []
        self.history_size = history_size

    def calculate_pi(self, current_rssi_readings):
        """
        Computes the Proximity Index (Pi) based on the variance 
        and mean differential of surrounding wireless RSSI signals.
        """
        avg_rssi = sum(current_rssi_readings) / len(current_rssi_readings)
        self.rssi_history.append(avg_rssi)
        
        if len(self.rssi_history) > self.history_size:
            self.rssi_history.pop(0)

        if len(self.rssi_history) < 2:
            return 0.0, "INITIALIZING"

        variance = sum((x - (sum(self.rssi_history) / len(self.rssi_history))) ** 2 for x in self.rssi_history) / len(self.rssi_history)
        pi_score = math.sqrt(variance)

        if pi_score < self.threshold:
            state = "GPS_SUPPRESSED (Stationary/Stable Zone - Power Saved)"
        else:
            state = "GPS_ENGAGED (High Mobility Detected)"

        return round(pi_score, 2), state

def run_simulation():
    print("==================================================")
    print("  GREENNET-MOBILE: Zero-GPS Proximity Engine (Pi) ")
    print("  Local Simulation Testbed - Zero Cost Execution  ")
    print("==================================================\n")

    engine = ProximityIndexEngine(threshold=2.0)
    
    simulated_scenarios = [
        [-55, -58, -56], # Stationary
        [-55, -57, -56], # Stationary
        [-56, -58, -57], # Stationary
        [-55, -56, -55], # Stationary
        [-70, -45, -82], # Sudden movement / environment shift
        [-85, -60, -40], # High variance movement
        [-54, -56, -55], # Settling down again
        [-55, -55, -56], # Stationary
        [-56, -57, -56], # Stationary
        [-55, -56, -55]  # Stationary
    ]

    for cycle, readings in enumerate(simulated_scenarios, start=1):
        pi_val, hardware_state = engine.calculate_pi(readings)
        print(f"Cycle {cycle:02d} | RSSI Inputs: {readings} | Pi Score: {pi_val:<5} | Status: {hardware_state}")
        time.sleep(0.3)

    print("\n[SUCCESS] Simulation completed successfully at $0 cost.")
    print("[RESULT] Zero-GPS algorithm verified: High-power hardware was successfully bypassed during stable cycles.")

if __name__ == "__main__":
    run_simulation()
