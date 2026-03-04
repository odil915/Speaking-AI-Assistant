from rich.console import Console
from core.brain import think
from core.memory import load_memory, save_memory

console = Console()

def get_mode():
    """
    Asks the user for the preferred interaction mode.
    """
    console.print("[bold cyan]Select Mode:[/bold cyan]")
    console.print("1. [green]T/T[/green] (Text Input / Text Output)")
    console.print("2. [green]O/T[/green] (Oral Input / Text Output)")
    console.print("3. [green]T/O[/green] (Text Input / Oral Output)")
    console.print("4. [green]O/O[/green] (Oral Input / Oral Output)")
    
    choice = console.input("[bold yellow]Choice (default T/T):[/bold yellow] ").strip().upper()
    
    if choice in ["2", "O/T"]:
        return "O/T"
    elif choice in ["3", "T/O"]:
        return "T/O"
    elif choice in ["4", "O/O"]:
        return "O/O"
    else:
        return "T/T"

def main():
    console.print("[bold green]Narrow AI Terminal[/bold green] (Type 'exit' to quit)")
    
    # 0. Select Mode
    mode = get_mode()
    input_type, output_type = mode.split('/')
    console.print(f"[dim]Mode set to: {mode} (Input: {input_type}, Output: {output_type})[/dim]")
    
    # 1. Initialize Memory (Load from Disk)
    history = load_memory()
    if history:
        console.print(f"[dim]Loaded {len(history)} past messages.[/dim]")
    
    # Lazy imports to avoid startup lag if not needed
    listen = None
    speak = None
    
    if input_type == "O":
        from core.ears import listen
    if output_type == "O":
        from core.mouth import speak
    
    while True:
        # 2. Input Handling
        user_input = ""
        
        if input_type == "O":
            # ORAL INPUT
            voice_text = listen()
            if voice_text:
                user_input = voice_text
                console.print(f"[bold yellow]You (Oral):[/bold yellow] {user_input}")
            else:
                # If silence, we can check for keyboard exit or just loop
                # To allow 'exit' via keyboard even in Oral mode:
                # But listen() blocks. For now, simple loop.
                continue
        else:
            # TEXT INPUT
            user_input = console.input("[bold yellow]You:[/bold yellow] ")

        # 🎤 Commands overriding mode
        if user_input.lower() in ["exit", "quit"]:
            console.print("[bold red]Goodbye![/bold red]")
            break
            
        if user_input.lower() == "clear memory":
            from core.memory import clear_memory
            clear_memory()
            history = []
            console.print("[bold red]Memory Wiped![/bold red]")
            continue

        # 🔄 Dynamic Mode Switching
        cmd = user_input.upper()
        new_mode = None
        
        if cmd in ["T/T", "TEXT MODE", "SWITCH TO TEXT", "DISABLE VOICE"]:
            new_mode = "T/T"
        elif cmd in ["O/O", "VOICE MODE", "FULL VOICE", "CALL MODE", "SWITCH TO VOICE"]:
            new_mode = "O/O"
        elif cmd in ["O/T", "DICTATION MODE", "I SPEAK", "INPUT VOICE"]:
            new_mode = "O/T"
        elif cmd in ["T/O", "READ TO ME", "OUTPUT VOICE", "SPEECH MODE"]:
            new_mode = "T/O"
            
        if new_mode:
            input_type, output_type = new_mode.split('/')
            console.print(f"[bold magenta]Switching Mode to: {new_mode}[/bold magenta]")
            
            # Ensure modules are loaded if switching to Oral
            if input_type == "O" and listen is None:
                from core.ears import listen
            if output_type == "O" and speak is None:
                from core.mouth import speak
            continue

        # 🎤 Commands overriding mode History
        history.append({'role': 'user', 'content': user_input})
            
        # 4. Think
        with console.status("[bold green]Thinking...[/bold green]", spinner="dots"):
            response = think(history)
            
        # 5. Output Handling
        console.print(f"[bold blue]AI:[/bold blue] {response}")
        
        if output_type == "O":
            # ORAL OUTPUT
            speak(response)
            
        history.append({'role': 'assistant', 'content': response})
        save_memory(history)
        console.print("-" * 50)

if __name__ == "__main__":
    main()
