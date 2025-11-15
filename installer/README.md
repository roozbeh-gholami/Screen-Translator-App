# Installer Setup

This directory contains the Inno Setup script to create an installer for Screen Translator.

## Prerequisites

Download and install Inno Setup from: https://jrsoftware.org/isinfo.php

## Building the Installer

1. Make sure you have built the executable first:
   ```
   pyinstaller app.spec
   ```

2. Open `setup.iss` with Inno Setup Compiler

3. Click "Build" -> "Compile" (or press Ctrl+F9)

4. The installer will be generated in `installer/output/` folder as:
   `ScreenTranslator_Setup_1.0.0.exe`

## What the Installer Does

- Installs Screen Translator to Program Files
- Creates Start Menu shortcuts
- Optional Desktop icon
- Includes uninstaller
- Bundles all dependencies (Tesseract-OCR, Python libraries)

## Customization

Edit `setup.iss` to customize:
- Version number (line 6)
- Publisher name (line 7)
- Installation directory
- Icons and shortcuts
