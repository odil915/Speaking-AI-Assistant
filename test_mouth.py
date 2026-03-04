import pyttsx3

def list_voices(engine):
    """Lists all available voices on the system."""
    voices = engine.getProperty('voices')
    print(f"Found {len(voices)} voices:")
    for index, voice in enumerate(voices):
        if 'ru' in voice.languages:
            print(f"{index}: ID: {voice.id}")
            print(f"   Name: {voice.name}")
            print(f"   Languages: {voice.languages}")
            print(f"   Gender: {voice.gender}")
            print("-" * 20)
    return voices

#print(list_voices(pyttsx3.init()))

def speak_russian(text):
    engine = pyttsx3.init()
    
    # 1. Inspect available voices
    print("--- Scanning for Russian Voices ---")
    voices = engine.getProperty('voices')
    russian_voice_id = None
    
    for voice in voices:
        # Heuristic to find Russian: Check name or languages property
        # Mac OS often uses 'ru_RU' in languages, or 'Yuri', 'Milena' in names
        is_russian_name = 'russian' in voice.name.lower() or 'sandy' in voice.name.lower() or 'sandy' in voice.name.lower()
        
        # Check languages safely
        is_russian_lang = False
        if hasattr(voice, 'languages') and voice.languages:
            langs_str = str(voice.languages).lower()
            if 'ja' in langs_str or 'ja_JP' in langs_str:
                is_russian_lang = True

        if is_russian_name or is_russian_lang:
            russian_voice_id = voice.id
            print(f"✅ Success! Found Russian voice: {voice.name}")
            break
            
    if russian_voice_id:
        engine.setProperty('voice', russian_voice_id)
        engine.setProperty('rate', 170) 
        
        print(f"🗣️  Speaking: {text}")
        engine.say(text)
        engine.runAndWait()
    else:
        print("❌ No specific Russian voice found.")
        print("Listing all available voices so you can choose manually if needed:")
        list_voices(engine)
        print("\nTIP: On macOS, go to System Settings > Accessibility > Spoken Content to add voices.")

if __name__ == "__main__":
    # Test text
    russian_text = "私の名前はオドルです"
    #speak_russian(russian_text)
