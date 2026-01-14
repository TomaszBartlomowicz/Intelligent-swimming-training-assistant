# Intelligent Swimming Training Assistant

## 🎯 Project Objective

The objective of this project is to develop a **wearable system** designed to enhance swimming training. The system provides **real-time monitoring** of a swimmer's physiological parameters and guides them through a structured training regimen. 

The system is composed of two main components:

### 1. Measurement Unit
A wearable device based on the **ESP32-C3** microcontroller, designed to be attached to swimming goggles or worn as a wristband. It continuously monitors:
- **Heart Rate (HR)**
- **Blood Oxygen Saturation (SpO₂)**
- **Battery Status** (via ADC monitoring)

### 2. Companion Application
A specialized application hosted on a **Raspberry Pi**, responsible for:
- Receiving data wirelessly from the measurement unit via **Bluetooth Low Energy (BLE)**
- Analyzing training progress in real-time
- Logging session data for future review
- Delivering instant feedback to the user through a graphical interface

---

## 🚀 Key Features
- **Training Planning** – Schedule personalized swimming sessions with specific goals.
- **Guided Training** – Follow workouts with live heart rate zones and progress tracking.
- **Historical Data Review** – Analyze past training sessions with detailed charts.
- **HRmax Calculator** – Automatically determine training zones based on your maximum heart rate.

---

## 🛠️ Tech Stack
- **Firmware:** C, ESP-IDF (FreeRTOS based)
- **Hardware Design:** KiCad (Custom PCB), I2C, BLE, ADC
- **Desktop App:** Python, PyQt5 (Qt Framework)
- **Data Processing:** Matplotlib, NumPy

---

## 📷 Preview
<img width="1280" alt="App Dashboard" src="https://github.com/user-attachments/assets/27c24d25-4538-40d5-a7df-10843922f756" />

<img width="1280" alt="Training View" src="https://github.com/user-attachments/assets/bc65400c-3e59-48c1-a797-3d4d17b8e500" />

---

## 📚 Sources & Assets
This project utilizes external assets for the user interface and background visuals:

* **Background Wallpapers:** Provided by [GetWallpapers](https://getwallpapers.com) (e.g., [Swimming Wallpaper](https://getwallpapers.com/wallpaper/full/9/6/b/1297710-beautiful-swimming-picsfor-wallpaper-2000x1260-phone.jpg)) [Accessed: 06.01.2026].
* **Icon Sets:** UI icons sourced from [Flaticon](https://www.flaticon.com) (Authors: Freepik, Pixel perfect, riajulislam, Uniconlabs, Iconjam) [Accessed: 06.01.2026].
* **System Icons:** "Information icon" via [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Information_icon.svg) [Accessed: 07.01.2026].
* **Reference Designs:** Training clock inspiration based on [SportClox](https://www.sportclox.com/View-AllClock/Speedo-4-Handed-Pace-Clock) (Euro Style Pace Clock) [Accessed: 07.01.2026].

---

## ⚖️ License
**Copyright © 2026 Tomasz Bartłomowicz. All rights reserved.**

No part of this project (source code, hardware designs, or documentation) may be used, reproduced, distributed, or modified in any form or by any means without the prior written permission of the author.
