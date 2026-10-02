# 🌱 GreenNet-Mobile

### An Eco-Friendly Interface Selection and Memory-Efficient Architecture for Reducing Mobile Energy Consumption

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23075915.svg)](https://doi.org/10.5281/zenodo.23075915)
[![Zenodo](https://img.shields.io/badge/Zenodo-Preprint-green)](https://zenodo.org/records/23075915)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

> **GreenNet-Mobile** is a software-defined, eco-friendly mobile networking framework designed to reduce unnecessary mobile energy consumption and contribute to longer hardware service life through intelligent interface selection, deterministic socket steering, and volatile-memory protection.

---

# 📖 Abstract

Modern mobile devices frequently activate cellular radio interfaces even when a lower-power local wireless interface is available. At the same time, conventional memory-management behavior may allow sensitive or temporary session data to be written to persistent storage through virtual-memory swapping.

**GreenNet-Mobile** addresses these two system-level concerns through a coordinated architecture combining:

1. **Zero-GPS Proximity Index (<i>P<sub>i</sub></i>)** — an RSSI-differential mechanism for identifying a sufficiently localized WLAN environment without relying on GPS.
2. **Kernel-Level Socket Steering** — deterministic binding of selected application sockets to the local WLAN interface using `SO_BINDTODEVICE`, reducing unnecessary cellular-interface activation.
3. **Volatile Memory Isolation** — use of POSIX `mlock()` for selected sensitive session buffers, combined with explicit zeroization at session termination, to prevent ordinary swapping of those locked pages.

The framework is designed around the principle that mobile energy efficiency can be improved at the software and operating-system interface level without requiring additional sensing hardware.

The manuscript reports **simulated benchmark evaluations** in which the modeled sensing current decreases from approximately **180 mA** for the baseline configuration to approximately **32 mA** for the GreenNet-Mobile configuration, corresponding to an approximately **82% reduction in the simulated evaluation**.

GreenNet-Mobile also investigates the relationship between volatile-memory handling, persistent-storage activity, and long-term device sustainability, with particular attention to NAND flash write activity and hardware service life.

> **Research status:** The reported performance figures are from the manuscript's simulated evaluation. Real-device measurements across mobile hardware, operating-system versions, radio chipsets, workloads, and network environments remain an important area for future validation.

---

# ⚙️ Extended System Architecture & Technical Description

GreenNet-Mobile integrates three principal mechanisms into a software-defined control pipeline:

```text
┌───────────────────────────────────────────────────────────────┐
│                    GREENNET-MOBILE                             │
│      Eco-Friendly Mobile Networking & Memory Architecture     │
└───────────────────────────────────────────────────────────────┘
                              │
                              ▼
                ┌───────────────────────────┐
                │  Environmental Interface  │
                │       Observation         │
                │                           │
                │  • WLAN RSSI              │
                │  • Cellular RSSI          │
                │  • Noise estimation       │
                └─────────────┬─────────────┘
                              │
                              ▼
                ┌───────────────────────────┐
                │ Zero-GPS Proximity Index   │
                │          Pᵢ               │
                │                           │
                │ RSSI differentials        │
                │ + weighted observations   │
                │ − noise component         │
                └─────────────┬─────────────┘
                              │
                         Pᵢ ≥ θthreshold
                              │
                              ▼
                ┌───────────────────────────┐
                │ Interface Selection       │
                │                           │
                │ Local WLAN available?     │
                └─────────────┬─────────────┘
                              │
                              ▼
                ┌───────────────────────────┐
                │ Kernel-Level Socket       │
                │ Steering                  │
                │                           │
                │ SO_BINDTODEVICE("wlan0")  │
                └─────────────┬─────────────┘
                              │
                              ▼
                ┌───────────────────────────┐
                │ Reduced Unnecessary       │
                │ Cellular Interface Use    │
                │                           │
                │       rmnet_data0         │
                │       ↓                   │
                │   lower activity          │
                └───────────────────────────┘


                ┌───────────────────────────┐
                │ Sensitive Session Data    │
                └─────────────┬─────────────┘
                              │
                              ▼
                ┌───────────────────────────┐
                │ POSIX mlock()             │
                │                           │
                │ Prevent ordinary swap-out │
                │ of selected memory pages  │
                └─────────────┬─────────────┘
                              │
                              ▼
                ┌───────────────────────────┐
                │ Session Termination       │
                │                           │
                │ Explicit 3-pass           │
                │ zeroization               │
                └─────────────┬─────────────┘
                              │
                              ▼
                ┌───────────────────────────┐
                │ Reduced Persistent-Storage │
                │ Exposure for Locked Data │
                └───────────────────────────┘
```

---

# 1. 📡 Zero-GPS RSSI Proximity Differential Engine

## 1.1 Objective

GreenNet-Mobile introduces a **Zero-GPS Proximity Index (<i>P<sub>i</sub></i>)** for determining whether a mobile device is sufficiently localized to a WLAN environment to justify preferential use of the local wireless interface.

The mechanism uses radio-signal observations rather than GPS coordinates.

This provides a software-defined method for estimating localized wireless proximity while avoiding dependence on satellite positioning.

---

### 1.2 Proximity Index

The framework defines the proximity index as:

$$P_i = \left( \sum_{k=1}^{K} (\text{RSSI}_k \cdot W_k) \right) - \Delta\text{Noise}$$

where:
* $P_i$ = calculated proximity index
* $\text{RSSI}_k$ = received signal-strength observation
* $W_k$ = normalized channel-stability weighting factor
* $K$ = number of observations
* $\Delta\text{Noise}$ = estimated dynamic background-variance component

The noise component is represented as:

$$\Delta\text{Noise} = \frac{1}{K} \sum_{k=1}^{K} \sigma_k^2$$

where $\sigma_k^2$ represents the estimated variance associated with the corresponding observation.

## 1.3 WLAN Validation

A localized WLAN environment is considered sufficiently suitable when:

$$
P_i \geq \theta_{threshold}
$$

where:

* <i>P<sub>i</sub></i> = calculated proximity index
* `θthreshold` = predefined decision threshold.

When the calculated index satisfies the threshold, the framework can proceed to preferential WLAN interface selection.

The purpose of this mechanism is not to provide geographical positioning. Instead, it provides a **local wireless-proximity decision signal** for interface-selection logic.

---

# 2. 🔌 Kernel-Level Deterministic Socket Steering

Once a suitable WLAN environment has been identified, GreenNet-Mobile uses deterministic socket steering to direct selected network traffic through the intended local interface.

The architecture uses the Linux socket option:

```c
setsockopt(
    sockfd,
    SOL_SOCKET,
    SO_BINDTODEVICE,
    "wlan0"
);
```

Here:

* `sockfd` = application socket descriptor
* `SOL_SOCKET` = socket-level option layer
* `SO_BINDTODEVICE` = interface-binding socket option
* `"wlan0"` = selected WLAN interface

The corresponding cellular interface is represented in the manuscript by:

```text
rmnet_data0
```

The architecture therefore establishes an explicit relationship between:

```text
Environmental Observation
        ↓
Proximity Decision
        ↓
Interface Selection
        ↓
Socket Steering
        ↓
Selected WLAN Interface
```

The manuscript describes this mechanism as forcing selected data transmission through `wlan0`, preventing fallback to the cellular interface and maintaining the cellular baseband modem in a DRX low-power sleep state.

> **Scope:** Actual radio power-state behavior depends on the operating system, device implementation, modem firmware, network stack, and hardware platform.

---

# 3. 🔒 POSIX `mlock()` Zeroization & NAND Flash Protection

GreenNet-Mobile also addresses persistent-storage activity associated with virtual-memory management.

Sensitive or temporary session data may be held in memory using POSIX `mlock()`:

```c
mlock(session_buffer, buffer_size);
```

The intended effect is to keep the selected memory pages resident and prevent them from being ordinarily swapped out to persistent storage.

The manuscript describes this mechanism as bypassing the operating-system page-swapping subsystem for the selected locked memory and reports **`Swapped Bytes = 0`** in the evaluated scenario.

---

## 3.1 Explicit Zeroization

At session termination, GreenNet-Mobile specifies explicit memory zeroization.

The manuscript describes a **three-pass zeroization process** for the relevant session buffer before memory release.

Conceptually:

```text
Active Session
      │
      ▼
Locked Session Buffer
      │
      │  mlock()
      ▼
Resident Memory
      │
      ▼
Session Termination
      │
      ▼
3-Pass Zeroization
      │
      ▼
Memory Release
```

The objective is to reduce residual session data in the relevant memory region after the session has ended.

---

## 3.2 Persistent-Storage Considerations

The architecture is motivated by the relationship between memory swapping and persistent storage.

When selected memory pages are locked, the framework's evaluated scenario avoids ordinary swap-out of those pages.

Accordingly, the manuscript reports:

```text
Swapped Bytes = 0
```

for the evaluated locked-memory configuration.

This should be understood specifically within that evaluation scenario. It does **not** mean that all operating-system storage writes are eliminated or that an entire device experiences zero NAND/UFS/NVMe writes.

---

# 📊 Performance Summary

The manuscript reports simulated benchmark results comparing baseline behavior with the GreenNet-Mobile architecture, including endpoint sensing current and storage-related behavior.

| Metric                            | Baseline Mobile OS / Configuration                    | GreenNet-Mobile Framework                                      | Reported / Targeted Effect                                      |
| --------------------------------- | ----------------------------------------------------- | -------------------------------------------------------------- | --------------------------------------------------------------- |
| **Sensing Current Draw**          | ≈180 mA baseline GNSS polling                         | ≈32 mA with Zero-GPS differential <i>P<sub>i</sub></i> sensing | **≈82% reduction in simulated evaluation**                      |
| **Cellular Modem Activity**       | Cellular radio activity during conventional operation | WLAN steering using `SO_BINDTODEVICE("wlan0")`                 | **Reduced unnecessary cellular-radio activity**                 |
| **Interface Control**             | Conventional interface selection                      | Deterministic socket-to-WLAN binding                           | **Explicit WLAN interface steering**                            |
| **NAND / Flash Storage Exposure** | Page-swapping behavior                                | Locked session-state memory using `mlock()`                    | **Swap writes targeted toward zero for locked memory**          |
| **Locked-Memory Swap Activity**   | Conventional swapping behavior                        | `Swapped Bytes = 0` in evaluated scenario                      | **No ordinary swap-out for evaluated locked pages**             |
| **GPS / GNSS Dependency**         | GNSS-based proximity sensing                          | RSSI-based Zero-GPS proximity mechanism                        | **GNSS hardware activation avoided for the proximity decision** |
| **Hardware Endurance Objective**  | Cumulative storage-write exposure                     | Memory isolation intended to reduce unnecessary swap writes    | **Reduced storage-wear objective**                              |
| **Sustainability Alignment**      | —                                                     | SDG 12 & SDG 13 aligned                                        | **Sustainability-oriented architecture**                        |

### Reported sensing-current comparison

The manuscript reports endpoint sensing current decreasing from approximately **180 mA** to approximately **32 mA** under the GreenNet-Mobile <i>P<sub>i</sub></i> evaluation scheme.

$$
Reduction =
\frac{180 - 32}{180}
\times 100
\approx 82.2\%
$$

Accordingly, the README reports this as an approximately **82% reduction in the simulated evaluation**.

> ⚠️ **Important:** This is a reported simulated benchmark result. It should not be interpreted as a universal 82% battery-life improvement across all mobile devices.

---

# 🧩 Key Technical Features

### 🌐 Zero-GPS Interface Selection

Uses RSSI-derived observations rather than GPS coordinates to support localized WLAN selection.

### 📡 RSSI Differential Analysis

Combines weighted signal observations and a noise component into the proximity index <i>P<sub>i</sub></i>.

### 🔌 Deterministic Socket Steering

Uses `SO_BINDTODEVICE` to explicitly associate selected sockets with the intended network interface.

### 📱 Cellular Activity Reduction Objective

Seeks to reduce unnecessary cellular-interface utilization when a suitable local WLAN path is available.

### 🔐 Volatile Memory Isolation

Uses POSIX `mlock()` for selected session buffers to prevent their ordinary swap-out.

### ⚡ Explicit Memory Zeroization

Applies a three-pass zeroization procedure to relevant session memory at session termination.

### 💾 Persistent-Storage Protection Objective

Investigates whether preventing unnecessary swapping of selected session data can reduce corresponding persistent-storage exposure and write activity.

### ♻️ Hardware Longevity Objective

Explores the relationship between reduced storage-write activity and longer flash-storage service life.

---

# 🛠️ Core Technical Components

| Component                            | Purpose                                            |
| ------------------------------------ | -------------------------------------------------- |
| <i>P<sub>i</sub></i> Proximity Index | Estimates localized WLAN suitability               |
| RSSI observation                     | Provides radio-signal input                        |
| `ΔNoise`                             | Accounts for observation variance/noise            |
| `θthreshold`                         | Defines WLAN-selection decision threshold          |
| `SO_BINDTODEVICE`                    | Provides deterministic socket-to-interface binding |
| `wlan0`                              | Representative WLAN interface                      |
| `rmnet_data0`                        | Representative cellular data interface             |
| `mlock()`                            | Keeps selected memory pages resident               |
| 3-pass zeroization                   | Clears selected session memory                     |
| Locked-memory evaluation             | Examines swap activity for selected memory         |

---

# 🔬 Evaluation Status

GreenNet-Mobile is presented as a **research framework with simulation-based evaluation**, rather than as a completed cross-device production benchmark.

The current work establishes the architectural concept and reports simulation-based comparisons.

Future validation should include real-device experiments across:

* Android and Linux-based mobile environments
* Different SoCs and modem architectures
* Multiple Wi-Fi chipsets
* Different cellular generations
* Diverse WLAN signal environments
* Different application workloads
* Background and foreground network activity
* Battery discharge measurements
* Modem power-state telemetry
* NAND/UFS storage-write measurements
* Memory-pressure conditions
* Different operating-system kernels

Such experiments would help determine how closely the simulated results correspond to physical-device behavior.

---

# 🌱 Sustainability Objectives

GreenNet-Mobile explores software-level mechanisms that may contribute to broader sustainability objectives through:

### ⚡ Energy Efficiency

Reducing unnecessary use of higher-power mobile radio interfaces when suitable local connectivity is available.

### 💾 Storage-Wear Reduction

Reducing unnecessary persistent-storage exposure associated with swapping of selected session data.

### 📱 Hardware Service Life

Exploring whether lower storage-write activity can contribute to reduced wear on flash-based storage.

### ♻️ E-Waste Reduction

Longer hardware service life may contribute to reduced replacement frequency and associated electronic waste.

### 🌍 UN SDG Alignment

The research is aligned with sustainability objectives associated with:

* **SDG 12 — Responsible Consumption and Production**
* **SDG 13 — Climate Action**

> These are research-alignment objectives and should not be interpreted as formal UN certification or endorsement.

---

# 🧭 Architecture at a Glance

```text
                    GREENNET-MOBILE
                           │
            ┌──────────────┴──────────────┐
            │                             │
            ▼                             ▼
      Radio Interface              Memory Management
         Analysis                       Control
            │                             │
            ▼                             ▼
       RSSI / Noise                   mlock()
            │                             │
            ▼                             ▼
     Proximity Index               Locked Pages
       Pᵢ ≥ θthreshold                   │
            │                            ▼
            ▼                       No Ordinary
      WLAN Selection                 Swap-Out
            │                            │
            ▼                            ▼
  SO_BINDTODEVICE("wlan0")        Session End
            │                            │
            ▼                            ▼
 Reduced Unnecessary              3-Pass Zeroization
 Cellular Activity                     │
            │                            ▼
            ▼                       Reduced Storage
    Energy Efficiency               Exposure Objective
            │
            └──────────────┬──────────────┘
                           ▼
                  Sustainable Mobile
                   Computing Objective
```

---

# 📚 Citation

If you use, discuss, extend, or reference this research, please cite the Zenodo preprint.

### Zenodo Preprint — Version 2

**GreenNet-Mobile: An Eco-Friendly Interface Selection and Memory-Efficient Architecture for Reducing Mobile Energy Consumption**

**DOI:**
https://doi.org/10.5281/zenodo.23075915

**Zenodo Record:**
https://zenodo.org/records/23075915

### BibTeX

```bibtex
@article{rashid2026greennetmobile,
  author  = {Rashid, Humayun},
  title   = {GreenNet-Mobile: An Eco-Friendly Interface Selection and Memory-Efficient Architecture for Reducing Mobile Energy Consumption},
  journal = {Zenodo Preprint},
  year    = {2026},
  doi     = {10.5281/zenodo.23075915},
  url     = {https://doi.org/10.5281/zenodo.23075915}
}
```

### Recommended Citation

> Rashid, H. (2026). *GreenNet-Mobile: An Eco-Friendly Interface Selection and Memory-Efficient Architecture for Reducing Mobile Energy Consumption*. Zenodo. https://doi.org/10.5281/zenodo.23075915

### DOI Information

**Version DOI:**
https://doi.org/10.5281/zenodo.23075915

**All-Versions DOI:**
https://doi.org/10.5281/zenodo.23030469

---

# 📑 References

1. IEEE Sustainable Computing Initiative. *Green Communications and Sustainable Computing Frameworks*. IEEE Transactions on Green Communications and Networking, 2024.

2. IEEE Computer Society. *POSIX.1-2017 Memory Management System Interfaces (mlock, munlock)*. IEEE Std 1003.1-2017, 2017.

3. United Nations Development Programme (UNDP). *Sustainable Development Goals: SDGs 12 and 13 Action Report*, 2023.

---

# 📜 Copyright & Licensing

**Copyright © 2026 Humayun Rashid (হুমায়ূন রশীদ). All rights reserved.**

The academic publication and associated documentation are released under the **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** license.

This permits appropriate non-commercial sharing and adaptation with attribution, subject to the terms of the license.

For commercial deployment, SDK integration, proprietary licensing, or other commercial arrangements, please contact the author.

> **License notice:** The CC BY-NC 4.0 license applies to material released under that license. Rights in any separately identified third-party material remain subject to their respective terms.

---

# 👤 Author

**Humayun Rashid (হুমায়ূন রশীদ — هُمايُون رَشِيد)**

Research Fellow
Department of Al-Fiqh and Law
Faculty of Law
Islamic University, Kushtia, Bangladesh

**Email:** [bd01889999898@gmail.com](mailto:bd01889999898@gmail.com)

**GitHub:** [HumayunRashidBD](https://github.com/HumayunRashidBD)

**LinkedIn:** [HumayunRashidBD](https://www.linkedin.com/in/HumayunRashidBD/)

---

# 🔗 Primary Research Record

### Zenodo Preprint — Version 2

**GreenNet-Mobile: An Eco-Friendly Interface Selection and Memory-Efficient Architecture for Reducing Mobile Energy Consumption**

**DOI:**
https://doi.org/10.5281/zenodo.23075915

**Zenodo Record:**
https://zenodo.org/records/23075915

**Published:** 2026

---

# 🎯 Research Status & Scope

GreenNet-Mobile is currently positioned as a **research architecture with simulation-based evaluation**.

The current publication establishes the architectural concept and reports simulated performance comparisons.

In particular:

* The approximately **82% reduction** is a reported simulated sensing-current comparison.
* The `Swapped Bytes = 0` observation applies to the evaluated locked-memory scenario.
* `mlock()` applies to selected locked memory pages rather than the entire operating system.
* `SO_BINDTODEVICE` provides socket-level interface binding; actual modem power-state behavior depends on the underlying operating system, modem, firmware, and hardware.
* Actual energy consumption depends on hardware, firmware, kernel behavior, radio conditions, workloads, and network configuration.
* Sustainability references to SDG 12 and SDG 13 describe research alignment and do not constitute formal certification or endorsement.

Real-device validation remains an important direction for subsequent research.

---

# 🌍 Project Positioning

GreenNet-Mobile focuses specifically on **mobile-endpoint energy efficiency and memory/storage behavior**.

Its technical scope centers on:

```text
Mobile Device
     │
     ├── Radio Interface Selection
     │       ├── RSSI
     │       ├── Proximity Index Pᵢ
     │       └── Socket Steering
     │
     └── Memory / Storage Behavior
             ├── mlock()
             ├── Zeroization
             └── Swap Avoidance Objective
```

The resulting research direction connects:

**mobile networking + operating-system interfaces + memory management + energy efficiency + storage sustainability**

within a single software-defined architecture.

---

# 📌 One-Sentence Summary

> **GreenNet-Mobile is a software-defined mobile sustainability architecture that combines zero-GPS RSSI-based interface selection, deterministic socket steering, and locked-memory session handling to investigate reductions in unnecessary mobile energy use and persistent-storage activity.**

---

## 📖 Primary Publication

**Humayun Rashid (2026)**
*GreenNet-Mobile: An Eco-Friendly Interface Selection and Memory-Efficient Architecture for Reducing Mobile Energy Consumption*

**Zenodo DOI:**
https://doi.org/10.5281/zenodo.23075915

**All-Versions DOI:**
https://doi.org/10.5281/zenodo.23030469

---

## ⚖️ License

**CC BY-NC 4.0 — Creative Commons Attribution-NonCommercial 4.0 International**

Copyright © 2026 **Humayun Rashid (হুমায়ূন রশীদ).**

For licensing, research collaboration, commercial deployment, or other inquiries, please contact the author.

---

> 🌱 **GreenNet-Mobile — Toward more energy-aware, memory-efficient, and sustainable mobile computing.**
