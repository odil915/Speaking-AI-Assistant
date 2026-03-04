import ollama
from rich.console import Console

console = Console()
console.print("[bold green]Asking the Brain...[/bold green]")

try:
    response = ollama.chat(model='phi4', messages=[
      {'role': 'user', 'content': 'Remember that my favourite color is green'},
    ])
    console.print(f"[bold blue]Brain says:[/bold blue] {response['message']['content']}")
    response = ollama.chat(model='phi4', messages=[
      {'role': 'user', 'content': 'What is my favourite color?'},
    ])
    console.print(f"[bold blue]Brain says:[/bold blue] {response['message']['content']}")
except Exception as e:
    console.print(f"[bold red]Error:[/bold red] {e}")
    console.print("[yellow]Did you pull the model? Try: ollama pull llama3.2[/yellow]")

