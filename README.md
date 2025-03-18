# Screen-Translator-App

Screen-Translator-App is a PyQt-based application that allows users to translate text within a draggable frame on their screen. The application utilizes **OpenCV**, **Pytesseract (OCR)**, and **Google Translate** to extract and translate text from images in real time.

## Features
- **Draggable Frame:** Select any area of the screen for text recognition.
- **Optical Character Recognition (OCR):** Uses Pytesseract to extract text from images.
- **Translation:** Automatically translates extracted text using Google Translate.
- **Cross-Platform Compatibility:** Primarily tested on Windows, but adaptable to other platforms.

## Installation

### Prerequisites
Ensure you have the following installed on your system:
- **Python 3.x**
- **pip** (Python package manager)
- **Tesseract-OCR** (Required for Pytesseract, [Download here](https://github.com/tesseract-ocr/tesseract))

### Install Dependencies
Clone the repository and install required dependencies:
```bash
 git clone https://github.com/roozbeh-gholami/Screen-Translator-App.git
 cd Screen-Translator-App
 pip install -r requirements.txt
```

## Usage
### Running the App (Windows)
Simply run the `run.bat` file to start the application:
```bash
 run.bat
```

### Running Manually
Alternatively, you can start the app manually with:
```bash
 python main.py
```

## Creating an Executable (Windows)
You can generate an executable file using **PyInstaller** with the provided `app.spec` file:
```bash
 pyinstaller app.spec
```
This will create an executable version of the application, which can be distributed without requiring Python installation.

## Contributing
Feel free to contribute to the project! Fork the repository, make changes, and submit a pull request.

## License
This project is licensed under the MIT License.

## Acknowledgments
- **PyQt** for GUI development
- **OpenCV** for image processing
- **Pytesseract** for OCR
- **Google Translate API** for translations


