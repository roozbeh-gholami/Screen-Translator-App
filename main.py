
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QSplashScreen, QAction, QMessageBox, QFileDialog 
from PyQt5 import QtCore, QtGui , QtSerialPort
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt, QTimer, QDateTime
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
        self.setupBoxUI()
        
        self.buttonBox.clicked.connect(self.onButtonClicked)
        self.translateBtn.clicked.connect(self.onTranslateBtnClicked)
    
    def setupBoxUI(self):
        """Enhanced box window UI setup"""
        # Update button text with icons
        self.translateBtn.setText("🔄 Translate")
        
        # Make window frameless but resizable
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        
        # Variables for dragging and resizing
        self.dragging = False
        self.resizing = False
        self.resize_edge = None
        self.drag_position = QPoint()
        self.resize_start_pos = QPoint()
        self.resize_start_geometry = QRect()
        
        # Enable mouse tracking for the window
        self.setMouseTracking(True)
        
        # Enable mouse tracking for all child widgets to ensure events propagate
        for child in self.findChildren(QWidget):
            child.setMouseTracking(True)
        
        # Update window title with size info
        self.update_size_info()
        
        # Set minimum size
        self.setMinimumSize(410, 310)

    def get_edge(self, pos):
        """Get which edge is being hovered for resizing"""
        margin = 12  # Increased margin for easier resize grabbing
        rect = self.rect()
        
        # Skip title bar area for resize detection
        if pos.y() <= 30:
            return None
        
        left = pos.x() <= margin
        right = pos.x() >= rect.width() - margin
        top = pos.y() <= margin + 30  # Account for title bar
        bottom = pos.y() >= rect.height() - margin
        
        if top and left:
            return 'top-left'
        elif top and right:
            return 'top-right'
        elif bottom and left:
            return 'bottom-left'
        elif bottom and right:
            return 'bottom-right'
        elif top:
            return 'top'
        elif bottom:
            return 'bottom'
        elif left:
            return 'left'
        elif right:
            return 'right'
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Check if click is in the title bar area (top 30px)
            if event.pos().y() <= 30:
                # Dragging from title bar
                self.dragging = True
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            else:
                # Check for resize edges only outside title bar
                edge = self.get_edge(event.pos())
                if edge:
                    self.resizing = True
                    self.resize_edge = edge
                    self.resize_start_pos = event.globalPos()
                    self.resize_start_geometry = self.geometry()
        
        event.accept()

    def mouseMoveEvent(self, event):
        if not (self.dragging or self.resizing):
            # Set cursor based on position
            edge = self.get_edge(event.pos())
            if edge:
                if edge in ['top', 'bottom']:
                    self.setCursor(Qt.SizeVerCursor)
                elif edge in ['left', 'right']:
                    self.setCursor(Qt.SizeHorCursor)
                elif edge in ['top-left', 'bottom-right']:
                    self.setCursor(Qt.SizeFDiagCursor)
                elif edge in ['top-right', 'bottom-left']:
                    self.setCursor(Qt.SizeBDiagCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
        
        if self.dragging:
            # Move window
            new_pos = event.globalPos() - self.drag_position
            self.move(new_pos)
            
        elif self.resizing:
            # Resize window
            self.resize_window(event.globalPos())
        
        event.accept()

    def resize_window(self, global_pos):
        """Resize the window based on mouse position"""
        delta = global_pos - self.resize_start_pos
        geometry = QRect(self.resize_start_geometry)
        
        if 'left' in self.resize_edge:
            geometry.setLeft(geometry.left() + delta.x())
        if 'right' in self.resize_edge:
            geometry.setRight(geometry.right() + delta.x())
        if 'top' in self.resize_edge:
            geometry.setTop(geometry.top() + delta.y())
        if 'bottom' in self.resize_edge:
            geometry.setBottom(geometry.bottom() + delta.y())
        
        # Ensure minimum size
        if geometry.width() < 410:
            if 'left' in self.resize_edge:
                geometry.setLeft(geometry.right() - 410)
            else:
                geometry.setRight(geometry.left() + 410)
        
        if geometry.height() < 310:
            if 'top' in self.resize_edge:
                geometry.setTop(geometry.bottom() - 310)
            else:
                geometry.setBottom(geometry.top() + 310)
        
        self.setGeometry(geometry)
        self.update_size_info()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.resizing = False
            self.resize_edge = None
            self.setCursor(Qt.ArrowCursor)
        
        event.accept()
    def onTranslateBtnClicked(self, event):
        """Enhanced translation button click with visual feedback"""
        self.img = [None]
        
        # Visual feedback - flash the window border
        self.setStyleSheet(self.styleSheet() + """
QDialog { border: 3px solid #28a745; }
""")
        QApplication.processEvents()
        
        # Define the bounding box more precisely - capture only the frame area
        frame_rect = self.frameLbl.geometry()
        dialog_pos = self.geometry()
        
        # Calculate the actual capture area (frame label area only)
        bbox = {
            'top': dialog_pos.y() + frame_rect.y(),
            'left': dialog_pos.x() + frame_rect.x(), 
            'width': frame_rect.width(),
            'height': frame_rect.height()
        }
        
        # Run the live box capture function with the defined bbox
        self.img[0] = liveScreenCapture(bbox)
        self.applySignal.emit(self.img[0])
        
        # Reset border style after visual feedback
        def reset_border():
            current_style = self.styleSheet()
            if 'QDialog { border: 3px solid #28a745; }' in current_style:
                self.setStyleSheet(current_style.replace('QDialog { border: 3px solid #28a745; }', ''))
        
        QTimer.singleShot(500, reset_border)
    
    def update_size_info(self):
        """Update window title with current size information"""
        size = self.size()
        self.setWindowTitle(f"📋 Capture Area - {size.width()}×{size.height()}px")
    
    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        self.update_size_info()

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
        self.setupUI()
        self.show()

        self.boxBtn.clicked.connect(self.boxButtonClicked)
        self.addItemComboBoxes()

    def setupUI(self):
        """Enhanced UI setup with modern styling and better UX"""
        # Set window properties
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        
        # Update button text with icons
        self.boxBtn.setText("🎯 Start Translation Capture")
        
        # Set placeholder text for translation area
        self.translatedTxt.setPlaceholderText("📝 Translated text will appear here...\n\n"
                                            "1. Click 'Start Translation Capture' to open capture window\n"
                                            "2. Drag the capture window over the text you want to translate\n"
                                            "3. Click 'Translate' to capture and translate the content")
        
        # Add status bar message
        self.statusbar.showMessage("Ready to translate - Select your languages and start capturing!")
        
        # Improve window appearance
        self.setWindowOpacity(0.95)
        
        # Add menu items
        self.setupMenus()

    def setupMenus(self):
        """Setup application menus"""
        # File menu
        fileMenu = self.menubar.addMenu('📁 File')
        
        # Add actions
        saveAction = QAction('💾 Save Translation', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.triggered.connect(self.saveTranslation)
        fileMenu.addAction(saveAction)
        
        fileMenu.addSeparator()
        
        exitAction = QAction('❌ Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)
        
        # Help menu
        helpMenu = self.menubar.addMenu('❓ Help')
        
        aboutAction = QAction('ℹ️ About', self)
        aboutAction.triggered.connect(self.showAbout)
        helpMenu.addAction(aboutAction)
        
        instructionsAction = QAction('📖 Instructions', self)
        instructionsAction.triggered.connect(self.showInstructions)
        helpMenu.addAction(instructionsAction)
        
        # Edit menu
        editMenu = self.menubar.addMenu('✏️ Edit')
        
        copyAction = QAction('📋 Copy Translation', self)
        copyAction.setShortcut('Ctrl+C')
        copyAction.triggered.connect(self.copyTranslation)
        editMenu.addAction(copyAction)
        
        clearAction = QAction('🗑️ Clear', self)
        clearAction.setShortcut('Ctrl+L')
        clearAction.triggered.connect(self.clearTranslation)
        editMenu.addAction(clearAction)
    
    def showAbout(self):
        """Show about dialog"""
        QMessageBox.about(self, "About Screen Translator", 
                         "🌐 Screen Translator v2.0\n\n"
                         "Real-time OCR and translation tool\n\n"
                         "Features:\n"
                         "• Live screen text capture\n"
                         "• Multi-language translation\n"
                         "• Modern dark theme UI\n"
                         "• Easy drag-and-drop interface\n\n"
                         "Powered by:\n"
                         "• Tesseract OCR\n"
                         "• Google Translate API\n"
                         "• PyQt5 Framework")
    
    def showInstructions(self):
        """Show instructions dialog"""
        QMessageBox.information(self, "How to Use Screen Translator",
                               "📖 Instructions:\n\n"
                               "1. Select source and target languages\n"
                               "2. Click 'Start Translation Capture'\n"
                               "3. Drag the capture window over text\n"
                               "4. Click 'Translate' to process\n"
                               "5. View results in the main window\n\n"
                               "💡 Tips:\n"
                               "  • Ensure good contrast for better OCR\n"
                               "  • Position capture window precisely\n"
                               "  • Internet required for translation\n"
                               "  • Supports 100+ languages")
    
    def saveTranslation(self):
        """Save current translation to a text file"""
        if not self.translatedTxt.toPlainText().strip():
            QMessageBox.warning(self, "No Translation", 
                              "⚠️ No translation available to save.\n\n"
                              "Please translate some text first!")
            return
            
        from PyQt5.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "💾 Save Translation",
            f"translation_{QDateTime.currentDateTime().toString('yyyy-MM-dd_hh-mm')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Screen Translator - Translation Export\n")
                    f.write(f"Generated: {QDateTime.currentDateTime().toString()}\n")
                    f.write(f"=" * 50 + "\n\n")
                    f.write(self.translatedTxt.toPlainText())
                
                QMessageBox.information(self, "Success", 
                                      f"✅ Translation saved successfully!\n\n"
                                      f"File: {filename}")
                self.statusbar.showMessage(f"Translation saved to {filename}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", 
                                   f"❌ Failed to save file:\n{str(e)}")
    
    def copyTranslation(self):
        """Copy current translation to clipboard"""
        text = self.translatedTxt.toPlainText()
        if text.strip():
            QApplication.clipboard().setText(text)
            self.statusbar.showMessage("📋 Translation copied to clipboard!")
        else:
            QMessageBox.information(self, "No Translation", 
                                  "⚠️ No translation available to copy.")
    
    def clearTranslation(self):
        """Clear the translation area"""
        if self.translatedTxt.toPlainText().strip():
            reply = QMessageBox.question(self, "Clear Translation", 
                                       "🗑️ Are you sure you want to clear the current translation?",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.translatedTxt.clear()
                self.statusbar.showMessage("Translation area cleared")
        else:
            self.translatedTxt.clear()

    def boxButtonClicked(self):
        """Enhanced box dialog with better positioning and styling"""
        # Update button text to show it's active
        self.boxBtn.setText("🔄 Capture Window Active...")
        self.boxBtn.setEnabled(False)
        
        # Update status
        self.statusbar.showMessage("Translation capture window opened - position it over the text to translate")
        
        #open dialog box
        self.boxDialog = boxWiindow(self)
        
        # Enhanced styling and transparency - more transparent to see through
        self.boxDialog.setWindowOpacity(0.7)
        self.boxDialog.setWindowTitle("📋 Translation Capture Area")
        
        # Set window attributes for transparency
        self.boxDialog.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # Better positioning - center on screen initially
        screen = QApplication.desktop().screenGeometry()
        dialog_width = 520
        dialog_height = 250
        x = (screen.width() - dialog_width) // 2
        y = (screen.height() - dialog_height) // 2
        self.boxDialog.setGeometry(x, y, dialog_width, dialog_height)

        # Set window flags for better behavior
        self.boxDialog.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        self.boxDialog.applySignal.connect(self.handleTranslateBtn)      
        
        # Show dialog and reset button when closed
        result = self.boxDialog.exec_()
        self.boxBtn.setText("🎯 Start Translation Capture")
        self.boxBtn.setEnabled(True)
        self.statusbar.showMessage("Ready to translate - Select your languages and start capturing!")
        
        # if dialog box is moved, print dialog box last location
        
        # if (boxDialog.exec_()==QDialog.Accepted):
            # pass
    def handleTranslateBtn(self, img):
        """Enhanced translation handling with better user feedback"""
        try:
            # Update UI to show processing
            if self.boxDialog:
                self.boxDialog.translateBtn.setText("🔄 Processing...")
                self.boxDialog.translateBtn.setEnabled(False)
            
            self.statusbar.showMessage("🔍 Extracting text from image...")
            QApplication.processEvents()  # Update UI immediately
            
            # Extract text from image
            text = pyt.image_to_string(img)
            print(f"extracted text: {text}")
            
            if not text.strip():
                self.translatedTxt.setPlainText("⚠️ No text detected in the captured area.\n\n"
                                              "Tips:\n"
                                              "• Make sure the text is clearly visible\n"
                                              "• Try adjusting the capture window size\n"
                                              "• Ensure good contrast between text and background")
                self.statusbar.showMessage("No text detected - try repositioning the capture window")
                return
            
            self.statusbar.showMessage("🔄 Translating text...")
            QApplication.processEvents()
            
            # Get language codes
            from_code = self.fromCBox.currentText().split(' - ')[1]
            to_code = self.toCBox.currentText().split(' - ')[1]
            
            # Translate text
            translated_text = self.translateTextLineByLine(text, from_code=from_code, to_code=to_code)
            
            # Display only the translated result
            self.translatedTxt.setPlainText(translated_text)
            self.statusbar.showMessage(f"✅ Translation completed: {from_code.upper()} → {to_code.upper()}")
            
            print("translation is finished")
            
        except Exception as ex:
            error_msg = f"❌ Translation Error: {str(ex)}\n\n"
            error_msg += "Please check:\n"
            error_msg += "• Internet connection for translation service\n"
            error_msg += "• Selected language pair is supported\n"
            error_msg += "• Text quality in captured area"
            
            self.translatedTxt.setPlainText(error_msg)
            self.statusbar.showMessage(f"Translation failed: {str(ex)}")
            print(f"Translation error: {ex}")
            
        finally:
            # Reset button state
            if self.boxDialog:
                self.boxDialog.translateBtn.setText("🔄 Translate")
                self.boxDialog.translateBtn.setEnabled(True)

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
        """Enhanced language selection with popular languages at top"""
        # Popular languages for quick access
        popular_languages = [
            ('english', 'en'), ('spanish', 'es'), ('french', 'fr'), 
            ('german', 'de'), ('italian', 'it'), ('portuguese', 'pt'),
            ('russian', 'ru'), ('chinese', 'zh'), ('japanese', 'ja'),
            ('korean', 'ko'), ('arabic', 'ar'), ('hindi', 'hi')
        ]
        
        # Get all available languages
        self.avaiableLanguages: dict = GOOGLE_LANGUAGES_TO_CODES,
        all_items = []
        popular_items = []
        defaultFrom = "spanish - es"
        defaultTo = "english - en"
        
        # Create popular language items first
        for name, code in popular_languages:
            if name in self.avaiableLanguages[0]:
                popular_items.append(f'{name} - {code}')
        
        # Add separator
        separator_items = ["─" * 30]
        
        # Add all other languages (excluding popular ones already added)
        for key, value in sorted(self.avaiableLanguages[0].items()):
            item = f'{key} - {value}'
            if value not in [code for _, code in popular_languages]:
                all_items.append(item)
        
        # Combine lists: Popular + Separator + All Others
        final_items = popular_items + separator_items + all_items
        
        # Clear and populate comboboxes
        self.fromCBox.clear()
        self.toCBox.clear()
        
        self.fromCBox.addItems(final_items)
        self.fromCBox.setCurrentText(defaultFrom)
        
        self.toCBox.addItems(final_items)
        self.toCBox.setCurrentText(defaultTo)
        
        # Add tooltips
        self.fromCBox.setToolTip("Select the source language of the text to translate")
        self.toCBox.setToolTip("Select the target language for translation")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    # splashLoadingScreen()
    Ui =  MainWindow()
    Ui.show()
    sys.exit(app.exec_())