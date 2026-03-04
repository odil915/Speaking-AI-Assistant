import speech_recognition as sr
from rich.console import Console

console = Console()

def listen():
    """
    Listens to the microphone and returns the text.
    Uses Google Speech Recognition (Online) for speed/simplicity in this step,
    OR we can switch to local Whisper if installed.
    """
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        console.print("[bold red]Recording... (Speak now)[/bold red]")
        # Adjust for ambient noise
        r.adjust_for_ambient_noise(source)
        try:
            # Listen for input
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            console.print("[dim]Transcribing...[/dim]")
            
            # Using Google for now (Fastest setup)
            # For purely offline: r.recognize_whisper(audio) (Requires 'openai-whisper')
            text = r.recognize_google(audio)
            
            console.print(f"[bold yellow]Heard:[/bold yellow] {text}")
            return text
            
        except sr.WaitTimeoutError:
            print("No speech detected.")
            return None
        except sr.UnknownValueError:
            print("Could not understand audio.")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
