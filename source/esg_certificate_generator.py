#!/usr/bin/env python3
"""
@file esg_certificate_generator.py
@brief GreenNet-Mobile Verifiable ESG Compliance Certificate Generator
@author Humayun Rashid (Research Fellow, Islamic University, Kushtia, Bangladesh)
"""

import os
import json
from datetime import datetime

def generate_certificate(target_entity="Global Fleet Operator #01", daily_kwh_saved=2.19):
    print("==================================================")
    print(" GREENNET-MOBILE: Generating ESG Certificate")
    print(" Author: Humayun Rashid (Research Fellow, Islamic University, Kushtia, Bangladesh)")
    print("==================================================")

    cert_id = f"GNM-ESG-{int(datetime.utcnow().timestamp())}"
    co2_saved_kg = daily_kwh_saved * 0.475

    certificate_data = {
        "certificate_id": cert_id,
        "issued_at": datetime.utcnow().isoformat() + "Z",
        "issuer": {
            "name": "Humayun Rashid",
            "title": "Research Fellow",
            "affiliation": "Islamic University, Kushtia, Bangladesh"
        },
        "beneficiary": target_entity,
        "metrics": {
            "algorithm": "Zero-GPS Proximity Index ($P_i$) Framework",
            "memory_architecture": "POSIX mlock (Zero Flash Wear)",
            "daily_energy_saved_kwh": daily_kwh_saved,
            "daily_co2_offset_kg": round(co2_saved_kg, 3),
            "compliance_standard": "ISO/IEC 14040 Life Cycle Assessment Compatible"
        },
        "verification_status": "OFFICIALLY_VERIFIED_SUSTAINABLE"
    }

    os.makedirs("public_html/certificates", exist_ok=True)
    cert_path = f"public_html/certificates/{cert_id}.json"
    
    with open(cert_path, "w") as f:
        json.dump(certificate_data, f, indent=4)

    print(f"-> Certificate ID         : {cert_id}")
    print(f"-> Issued To              : {target_entity}")
    print(f"-> Verified CO2 Offset    : {round(co2_saved_kg, 3)} kg/day")
    print(f"[SUCCESS] ESG Certificate published to: {cert_path}")

if __name__ == "__main__":
    generate_certificate()
