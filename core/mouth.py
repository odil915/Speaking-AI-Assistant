import pyttsx3

def speak(text):
    """
    Converts text to speech using the local engine.
    """
    engine = pyttsx3.init()
    
    # Optional: Adjust rate (speed) and volume
    engine.setProperty('rate', 200)  # Speed percent (can go over 100)
    engine.setProperty('volume', 1.0)  # Volume 0-1

    engine.say(text)
    engine.runAndWait()
