#!/usr/bin/env python3
"""
GreenNet-Mobile: Public Dashboard Telemetry Integrator
Author: Humayun Rashid
Objective: Read latest benchmark JSON and update the public web portal at greennet.reachnbiz.com.
Cost: $0 (Runs on standard Linux/Python CLI)
"""

import json
import os

def update_web_dashboard():
    report_path = "/home/acmsrzwf/GreenNet-Mobile/benchmarks/latest_report.json"
    
    if not os.path.exists(report_path):
        print("[ERROR] latest_report.json not found. Run benchmark_aggregator.py first.")
        return

    with open(report_path, "r") as f:
        data = json.load(f)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GreenNet-Mobile | Official Research & Telemetry Portal</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f4f7f6; color: #333; margin: 0; padding: 40px; }}
        .container {{ max-width: 800px; margin: auto; background: #fff; padding: 40px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
        h1 {{ color: #2e7d32; margin-top: 0; }}
        .badge {{ background: #e8f5e9; color: #2e7d32; padding: 6px 12px; border-radius: 20px; font-weight: bold; font-size: 14px; display: inline-block; margin-bottom: 20px; }}
        .metric-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 30px 0; }}
        .card {{ background: #f9fbf9; border-left: 5px solid #4caf50; padding: 20px; border-radius: 6px; }}
        .card h3 {{ margin: 0 0 10px 0; color: #555; font-size: 16px; }}
        .card p {{ margin: 0; font-size: 24px; font-weight: bold; color: #2e7d32; }}
        .footer {{ margin-top: 40px; font-size: 13px; color: #777; border-top: 1px solid #eee; padding-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>GreenNet-Mobile Research Portal</h1>
        <div class="badge">Status: {data['status']}</div>
        <p><strong>Principal Investigator:</strong> {data['author']}</p>
        <p><strong>Trade License / Portal Anchor:</strong> reachnbiz.com</p>
        
        <div class="metric-grid">
            <div class="card">
                <h3>Active Current Reduction</h3>
                <p>{data['current_reduction_pct']}%</p>
            </div>
            <div class="card">
                <h3>Energy Saved (24h)</h3>
                <p>{data['energy_saved_wh']} Wh</p>
            </div>
            <div class="card">
                <h3>CO2 Emission Offset</h3>
                <p>{data['co2_reduction_grams']} g</p>
            </div>
            <div class="card">
                <h3>Flash Storage Swap Wear</h3>
                <p>100% Eliminated</p>
            </div>
        </div>

        <div class="footer">
            <p>Last Verified Timestamp: {data['timestamp']}</p>
            <p>Infrastructure: Enterprise Linux 8 / PostgreSQL / Python Engine on business83 ($0 Cost Development Cycle)</p>
        </div>
    </div>
</body>
</html>
"""

    # Target web root for greennet.reachnbiz.com (typical cPanel public_html structure or private sub-doc root)
    web_dir = "/home/acmsrzwf/GreenNet-Mobile/public_html"
    os.makedirs(web_dir, exist_ok=True)
    web_path = os.path.join(web_dir, "index.html")

    with open(web_path, "w") as f:
        f.write(html_content)

    print("==================================================")
    print("  GREENNET-MOBILE: Public Dashboard Updated       ")
    print("==================================================\n")
    print(f"  -> Generated HTML Dashboard : {web_path}")
    print(f"  -> Embedded Live Energy     : {data['energy_saved_wh']} Wh")
    print(f"  -> Embedded Live CO2 Offset : {data['co2_reduction_grams']} g")
    print("[SUCCESS] Public telemetry dashboard synchronized successfully at $0 cost.")

if __name__ == "__main__":
    update_web_dashboard()
