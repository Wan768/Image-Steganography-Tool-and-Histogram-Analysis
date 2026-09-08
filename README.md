# Image-Steganography-Tool-and-Histogram-Analysis-Python

A spatial-domain image steganography application that embeds and extracts arbitrary secret files (`.txt`, `.pdf`, `.png`, `.jpg`, etc.) using Least Significant Bit (LSB) substitution. Includes an RGB histogram comparison script to verify visual and statistical imperceptibility.

---

## Features

- **Format-Agnostic File Hiding:** Uses a structured binary metadata header to preserve original file extensions and file sizes automatically.
- **Graphical User Interface (GUI):** Dual tab Tkinter interface for encoding and decoding workflows.
- **Lossless Stego Export:** Enforces `.png` output to prevent transform domain compression artifacts (e.g., JPEG quantization) from corrupting embedded bits.
- **Statistical Quality Analysis:** Standalone histogram script to compare cover vs. stego color distribution channels.

---

## Prerequisites & Installation

### Set Up Virtual Environment

**Windows (PowerShell):**

`python -m venv .venv` 

`.\.venv\Scripts\activate`

### Install the required dependencies

`pip install -r requirements.txt`

### Both analyze_result.py and stego_tool.py are run separately. To run them,

`python stego_tool.py`

`python analyze_result.py`
