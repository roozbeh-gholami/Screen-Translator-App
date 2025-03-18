
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QSplashScreen 
from PyQt5 import QtCore, QtGui , QtSerialPort
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUiType

import resources_rc
import sys
import cv2
import numpy as np
import mss
import pytesseract as pyt
from deep_translator import GoogleTranslator
from deep_translator.constants import GOOGLE_LANGUAGES_TO_CODES
import os


def loadUiClass(path):
    stream = QFile(path)
    stream.open(QFile.ReadOnly)
    try:
        return loadUiType(stream)[0]
    finally:
        stream.close()

# Function to capture and display the screen continuously
def liveScreenCapture(bbox, close=False):
    img = [None]
    # get current location of py file
    py_location = os.path.dirname(os.path.realpath(__file__))
    # set the path to tesseract.exe
    pyt.pytesseract.tesseract_cmd = os.path.join(py_location, 'Tesseract-OCR', 'tesseract.exe')
    with mss.mss() as sct:
        if not close:
        # while True:
            # Capture the specific region defined by bbox
            screenshot = sct.grab(bbox)
            
            # Convert the screenshot to a numpy array
            img = np.array(screenshot)
                       
            # Convert colors from BGRA to BGR (which OpenCV expects)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            # Display the image in a window
            # cv2.imshow('Live Box Capture', img)

            # Break the loop if 'q' key is pressed
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
        else:
            # Close the window
            cv2.destroyAllWindows()
        return img


class boxWiindow(QDialog, loadUiClass(':/ui_files/boxWindow.ui')):
    applySignal = pyqtSignal(np.ndarray)
    def __init__(self, parent=None):
        super().__init__(parent)       
        self.setupUi(self)
        
        self.is_dragging = False
        self.click_offset = QPoint()
        self.buttonBox.clicked.connect(self.onButtonClicked)

        self.translateBtn.clicked.connect(self.onTranslateBtnClicked)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.click_offset = event.globalPos() - self.frameGeometry().topLeft()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            new_pos = event.globalPos() - self.click_offset
            self.move(new_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        return
        if event.button() == Qt.LeftButton:
            self.img = [None]
            self.is_dragging = False
            print(f"DialogBox position {self.geometry()}")
            # Define the bounding box (bbox) as a dictionary with left, top, width, and height
            bbox = {'top': self.geometry().y()+10 , 'left': self.geometry().x()+10, 'width': self.geometry().width()-20, 'height': self.geometry().height()-60}

            # Run the live box capture function with the defined bbox
            self.img[0] = liveScreenCapture(bbox)
        super().mouseReleaseEvent(event)
    def onTranslateBtnClicked(self, event):
        self.img = [None]
        # Define the bounding box (bbox) as a dictionary with left, top, width, and height
        bbox = {'top': self.geometry().y()+10 , 'left': self.geometry().x()+10, 'width': self.geometry().width()-20, 'height': self.geometry().height()-60}
        # Run the live box capture function with the defined bbox
        self.img[0] = liveScreenCapture(bbox)
        self.applySignal.emit(self.img[0])

    def onButtonClicked(self, button):
        img = [None]
        standardBtn = self.buttonBox.standardButton(button)
        if standardBtn == QDialogButtonBox.Close:
            img[0] = liveScreenCapture(bbox=None, close=True)


    # def moveEvent(self, event):
    #     print(f"event type: {event.type}")
    #     # Get the last position of the dialog
    #     last_position = self.pos()
    #     print(f"Dialog last location: {last_position}")
    #     super().moveEvent(event)


class MainWindow (QMainWindow, loadUiClass(':/ui_files/mainWindow.ui')):
    def __init__(self):
        super( MainWindow, self).__init__()

        self.setupUi(self)
        self.boxDialog = None
        self.show()

        self.boxBtn.clicked.connect(self.boxButtonClicked)
        self.addItemComboBoxes()

           

    def boxButtonClicked(self):
        
        #open dialog box
        self.boxDialog = boxWiindow(self)
        # set dialog box transparency
        self.boxDialog.setWindowOpacity(0.7)
        # set dialog box background color
        self.boxDialog.setStyleSheet("QLabel{background-color: darkgray;border: 4px solid red;}")
        # set dialog box title
        self.boxDialog.setWindowTitle("Translator")
        
        # set dialog box geometry based on mainWindow geometry and add 100 to location
        self.boxDialog.setGeometry(self.geometry().x()+self.geometry().width() + 10, self.geometry().y(), self.boxDialog.geometry().width(), self.boxDialog.geometry().height())


        self.boxDialog.applySignal.connect(self.handleTranslateBtn)      


        self.boxDialog.exec_()
        
        # if dialog box is moved, print dialog box last location
        
        # if (boxDialog.exec_()==QDialog.Accepted):
            # pass
    def handleTranslateBtn(self, img):
        try:
            # self.boxDialog.translateBtn.setText("Translating...")
            text = pyt.image_to_string(img)
            print("translation is started")
            # Call the function to translate the text
            from_code = self.fromCBox.currentText().split(' - ')[1]
            to_code = self.toCBox.currentText().split(' - ')[1]
            translated_text = self.translateTextLineByLine(text, from_code = from_code, to_code = to_code)
            print("translation is finished")
            self.translatedTxt.setText(translated_text)
            # self.boxDialog.translateBtn.setText("Translate")
        except Exception as ex:
            self.boxDialog.translateBtn.setText("Translate")
            self.translatedTxt.setText("Null")
            print(f"ex: {ex}")

    def translateTextLineByLine(self,text, from_code = "es", to_code = "en"):
                
        text = text.replace("Press 'q' to Close", "")

        lines = text.split('\n')
        
        # Translate each line
        translated_lines = []
        for line in lines:
            if len(line) > 2:
                try:
                    translated = ""
                    translated = GoogleTranslator(source=from_code, target=to_code).translate(line)
                    # print(f"Original: {line.strip()}\nTranslated: {translated}\n")
                    translated_lines.append(translated)
                except Exception as ex:
                    print(f'line: {line}')
                    print(f'exception: {ex}')

        # Join the translated lines into a single string
        translated_text = '\n'.join(translated_lines)
        return translated_text
    
    def addItemComboBoxes(self):
        # add available languages from google translator api to a list
        self.avaiableLanguages: dict = GOOGLE_LANGUAGES_TO_CODES,
        items = []
        defaultFrom = ""
        defaultTo = ""
        # pair the language code with the language name and add to items list
        for key, value in self.avaiableLanguages[0].items():
            items.append(f'{key} - {value}')
            # es - spanish, en - english are the default languages
            if value == 'es':
                defaultFrom = f'{key} - {value}'
            elif value == 'en':
                defaultTo = f'{key} - {value}'
        
        # clear the comboboxes
        self.fromCBox.clear()
        self.toCBox.clear()

        self.fromCBox.addItems(map(str, items))
        # set the default languages
        self.fromCBox.setCurrentText(defaultFrom)
        self.toCBox.addItems(map(str, items))
        self.toCBox.setCurrentText(defaultTo)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    # splashLoadingScreen()
    Ui =  MainWindow()
    Ui.show()
    sys.exit(app.exec_())