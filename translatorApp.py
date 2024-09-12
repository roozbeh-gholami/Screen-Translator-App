import cv2
import numpy as np
import mss
import tkinter as tk
from tkinter import ttk
import pytesseract as pyt
from deep_translator import GoogleTranslator


def closeWindow(event, root):
    if event.char == 'q':
        root.destroy()

def closeWindowBtn(root):
    root.destroy() 

# Function to capture and display the screen continuously
def liveScreenCapture(bbox, close=False):
    pyt.pytesseract.tesseract_cmd = r"\Tesseract-OCR\tesseract.exe"
    with mss.mss() as sct:
        if ~close:
        # while True:
            # Capture the specific region defined by bbox
            screenshot = sct.grab(bbox)
            
            # Convert the screenshot to a numpy array
            img = np.array(screenshot)
            
            

            # Convert colors from BGRA to BGR (which OpenCV expects)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            # Display the image in a window
            cv2.imshow('Live Box Capture', img)

            # Break the loop if 'q' key is pressed
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
        else:
            # Close the window
            cv2.destroyAllWindows()
        return img


# Function to create a second window and position it at the bottom of the main window
def createSecondWindow(root):
    secondWindow = tk.Toplevel(root)
    secondWindow.overrideredirect(True)
    secondWindow.title("Second Window")
    root.update()
    # Get the main window's position and size
    main_x = root.winfo_x()
    main_y = root.winfo_y()
    main_height = root.winfo_height()
    secondWindowHeight = int(root.winfo_height()/2)
    secondWindowWidth = root.winfo_width()
    
    secondWindow.geometry(f'{secondWindowWidth}x{secondWindowHeight}+{main_x}+{main_y + secondWindowHeight}')
    # Set the transparency of the second window
    secondWindow.attributes('-alpha', 1.0)
    # Create a frame to hold the bottom half of the window
    bottom_frame = tk.Frame(secondWindow, height=main_height/2, width=secondWindowWidth)
    bottom_frame.pack(fill="both")
    bottom_frame.update()
    # Create a Text widget 
    textbBoxTranslattion = tk.Text(bottom_frame, height=bottom_frame.winfo_height()-2, width=secondWindowWidth-5)
    textbBoxTranslattion.pack(fill="both")


    return secondWindow, textbBoxTranslattion

def drawRectangle():
    
    def translateTextLineByLine(text, from_code = "en", to_code = "es"):
                
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
    
    def mouseReleased(event, img, textbBoxTranslattion):
        print("Button released and additional function executed")
        try:
            text = pyt.image_to_string(img)
            
            
            # Call the function to translate the text
            translated_text = translateTextLineByLine(text, from_code = "en", to_code = "es")
            # delete text in the Text widget
            textbBoxTranslattion.delete("1.0", tk.END)
            # insert text in the beginning of the Text widget
            textbBoxTranslattion.insert("1.0", translated_text)
            # print(f"translated text: \n {translated_text}")
        except Exception as ex:
            print(f"img: {img}")
            print(f"ex: {ex}")
            

    # Function to handle mouse dragging to move the window
    def startDrag(event, textbBoxTranslattion, secondWindow, width, height, ):
        img = [None]
        # Get the initial position of the mouse
        x = event.x
        y = event.y
        start_x = event.x_root
        start_y = event.y_root     
        preDict = {"dx" : 0, "dy" : 0}
        # Function to handle mouse motion
        def onMotion(event):
            
            # Calculate the movement offset
            dx = event.x_root - start_x
            dy = event.y_root - start_y

            winX = start_x - x
            winY = start_y - y
            preDict["dx"] = dx - preDict["dx"]
            preDict["dy"] = dy - preDict["dy"]

            # Update the window position
            root.geometry(f"{width}x{int(height*2)}+{winX + dx}+{winY + dy}")
            root.update()
            secondWindow.geometry(f"{width}x{int(height*2)}+{winX + dx}+{winY + dy + int(height)}")
            secondWindow.update()
            # Define the bounding box (bbox) as a dictionary with left, top, width, and height
            bbox = {'top': winY + dy, 'left': winX + dx, 'width': int(width), 'height': int(height)}

            # Run the live box capture function with the defined bbox
            img[0] = liveScreenCapture(bbox)
            
            

        # Bind motion event and capture the release of the mouse button
        root.bind('<Motion>', onMotion)
        # Existing binding with the lambda function to unbind <Motion>
        root.bind('<ButtonRelease-1>', lambda event: [root.unbind('<Motion>'), mouseReleased(event, img[0], textbBoxTranslattion)])

    # Create the main window
    root = tk.Tk()

    # Set window attributes to make it transparent
    root.attributes('-alpha', 0.3)  # Set transparency level (0.0 to 1.0)
    root.overrideredirect(True)  # Remove window decorations (title bar, borders, etc.)
    width = 400
    height = 300
    # Set the window size and position
    root.geometry(f'{width}x{height}+100+100')  # Width x Height + X Offset + Y Offset
    
    # Create a frame to act as the window border
    top_border_frame = tk.Frame(root, bg='red', width=width, height=height/2, borderwidth=5)
    top_border_frame.pack(side="top", fill="x")
    top_border_frame.pack_propagate(False)  # Prevent frame from resizing

    # Place the border frame at (0, 0) relative to root
    top_border_frame.place(x=0, y=0)
    
    # Create a label to display some text in the window
    topLabel = tk.Label(top_border_frame)
    topLabel.pack(expand=True, fill='both')
    
    closeBtn = tk.Button(root, text="Close", command=lambda :closeWindowBtn(root),  bg="black", fg="white", font=("Arial", 12, "bold")) 
    
    closeBtn.place(x=15, y=height/2) 

    secondWindow, textbBoxTranslattion = createSecondWindow(root)

    # Create a frame to hold the bottom half of the window
    bottom_frame = tk.Frame(root, height=height/2, width=width)
    bottom_frame.pack(side="bottom", fill="both")
    # Create a label to display some text in the window
    label = tk.Label(bottom_frame, text="Press 'q' to Close", font=("Arial", 14), bg='white', anchor="n")
    label.pack(expand=True, fill='both')
    # label.place(x=450, y=350)
    # Create a Text widget 
    # textbBoxTranslattion = tk.Text(bottom_frame, height=5, width=width-5)
    # textbBoxTranslattion.pack(fill="both")

    # Bind the 'q' key to the close_window function
    root.bind('<Key>', lambda event:closeWindow(event, root))
    # Bind mouse button press to start dragging the window
    topLabel.bind('<ButtonPress-1>', lambda event:startDrag(event, textbBoxTranslattion, secondWindow, width=width, height=height/2))

    

    # Run the Tkinter event loop
    root.mainloop()
    

def main():
    drawRectangle()
    print("Press q to exit")
    


if __name__=="__main__":
    main()