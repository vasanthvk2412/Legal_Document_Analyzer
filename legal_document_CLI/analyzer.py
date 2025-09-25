import os
import argparse
import google.generativeai as genai
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.box import ROUNDED
from rich.align import Align
from rich import box
from speaker import speak_text
import PyPDF2
import speech_recognition as sr

# --- SETUP ---
console = Console()
tts_enabled = True   # Default: Text-to-Speech is ON
last_explanation = ""  # Store last explanation for replay


def configure_api():
    """Configures the API key by hardcoding it in the script."""
    try:
        api_key = "PASTE_YOUR_API_KEY_HERE"  
        if not api_key or api_key == "PASTE_YOUR_API_KEY_HERE":
            raise ValueError("API key not found.")
        genai.configure(api_key=api_key)
        return True
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        return False


# --- HELPERS ---
def read_pdf_text(filepath):
    """Extracts text from a PDF file."""
    text = ""
    try:
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        console.print(f"[bold red]PDF Error:[/bold red] {e}")
    return text


def read_text_file(filepath):
    """Reads text from a normal .txt file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        console.print(f"[bold red]File Error:[/bold red] {e}")
        return ""


def translate_text(text, target_language, task="translate"):
    """Translates text using Gemini."""
    action = "Translate" if task == "translate" else "Translate and simplify"
    try:
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        prompt = f"{action} the following text to {target_language}. Only provide the resulting text:\n\n{text}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        console.print(f"[bold red]Translate Error:[/bold red] {e}")
        return text


def perform_analysis(original_doc_text, english_doc, user_question, source_language):
    """Analyzes English doc but extracts source from original."""
    prompt = f"""
    You are a precise legal assistant. Answer the user's question based ONLY on the provided English document.
    Then, extract the exact source sentence(s) from the ORIGINAL document text ({source_language}).

    --- ENGLISH DOCUMENT TEXT START ---
    {english_doc}
    --- ENGLISH DOCUMENT TEXT END ---

    --- ORIGINAL DOCUMENT TEXT START ---
    {original_doc_text}
    --- ORIGINAL DOCUMENT TEXT END ---

    User Question: "{user_question}"

    Required format:
    **Explanation (English):**
    [Your simplified English answer here]

    **Source from original document ({source_language}):**
    "[Exact quoted sentence(s) from the original document]"
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content(prompt)
        parts = response.text.split("**Source from original document")
        explanation = parts[0].replace("**Explanation (English):**", "").strip()
        source = parts[1].split("**")[-1].strip() if len(parts) > 1 else "Source not found."
        return explanation, source
    except Exception as e:
        console.print(f"[bold red]Analysis Error:[/bold red] {e}")
        return "Could not process the request.", "Error."


def analyze_document_multilingual(original_doc_text, user_question, source_language):
    """Workflow: translate if needed, analyze, and return answer + source."""
    if source_language.lower() == "english":
        english_doc = original_doc_text
    else:
        english_doc = translate_text(original_doc_text, "English")

    english_explanation, original_source = perform_analysis(
        original_doc_text, english_doc, user_question, source_language
    )

    final_explanation = translate_text(
        english_explanation, source_language, task="translate and simplify"
    )

    return final_explanation, original_source


def speech_to_text(lang="en-IN"):
    """Captures speech and converts to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        console.print(Panel("🎤 Listening... please speak your question", style="cyan", border_style="blue", box=ROUNDED))
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=20)
    try:
        text = recognizer.recognize_google(audio, language=lang)
        console.print(Panel(f"✅ You said:\n[bold green]{text}[/bold green]", border_style="green", box=ROUNDED))
        return text
    except Exception:
        console.print(Panel("❌ Could not understand audio", style="red", border_style="red", box=ROUNDED))
        return ""


# --- MENU ---
def menu_loop(document_text, source_language):
    global tts_enabled, last_explanation
    while True:
        table = Table(title="📌 Main Menu", box=box.ROUNDED, style="bold cyan")
        table.add_column("Option", style="magenta", justify="center")
        table.add_column("Description", style="green")

        table.add_row("1", "Ask a question (type)")
        table.add_row("2", "Ask a question (voice)")
        table.add_row("3", "Change language")
        table.add_row("4", "Replay last explanation")
        table.add_row("5", f"Toggle Text-to-Speech (Currently {'ON' if tts_enabled else 'OFF'})")
        table.add_row("6", "Exit")

        console.print(table)

        choice = console.input("[magenta]👉 Enter choice: [/magenta] ")

        if choice == "1":
            question = console.input("[bold magenta]> Your question: [/bold magenta]")
            if question.strip():
                explanation, source = analyze_document_multilingual(document_text, question, source_language)
                last_explanation = explanation
                output_panel = Panel(
                    f"[bold yellow]Explanation:[/bold yellow]\n{explanation}\n\n[bold cyan]Source:[/bold cyan]\n[i]\"{source}\"[/i]",
                    title="💡 AI Analysis",
                    border_style="green",
                    expand=True,
                    box=ROUNDED
                )
                console.print(output_panel)
                if tts_enabled:
                    speak_text(explanation, lang=source_language.lower()[:2])

        elif choice == "2":
            spoken_q = speech_to_text(lang=source_language.lower()[:2])
            if spoken_q:
                explanation, source = analyze_document_multilingual(document_text, spoken_q, source_language)
                last_explanation = explanation
                output_panel = Panel(
                    f"[bold yellow]Explanation:[/bold yellow]\n{explanation}\n\n[bold cyan]Source:[/bold cyan]\n[i]\"{source}\"[/i]",
                    title="💡 AI Analysis",
                    border_style="green",
                    expand=True,
                    box=ROUNDED
                )
                console.print(output_panel)
                if tts_enabled:
                    speak_text(explanation, lang=source_language.lower()[:2])

        elif choice == "3":
            new_lang = console.input("[cyan]🌐 Enter new language (e.g., Tamil, Hindi, English): [/cyan]")
            if new_lang.strip():
                source_language = new_lang.strip()
                console.print(Panel(f"✅ Language changed to {source_language}", border_style="blue", box=ROUNDED))

        elif choice == "4":
            if last_explanation:
                console.print(Panel(f"[yellow]Replaying last explanation:[/yellow]\n{last_explanation}", border_style="yellow", box=ROUNDED))
                if tts_enabled:
                    speak_text(last_explanation, lang=source_language.lower()[:2])
            else:
                console.print(Panel("❌ No explanation available yet", border_style="red", box=ROUNDED))

        elif choice == "5":
            tts_enabled = not tts_enabled
            status = "ON ✅" if tts_enabled else "OFF ❌"
            console.print(Panel(f"🔊 Text-to-Speech is now {status}", border_style="blue", box=ROUNDED))

        elif choice == "6":
            console.print(Panel("👋 Goodbye! See you again.", border_style="yellow", box=ROUNDED))
            break
        else:
            console.print(Panel("❌ Invalid choice, please try again.", border_style="red", box=ROUNDED))


# --- MAIN ---
def main():
    if not configure_api():
        return

    parser = argparse.ArgumentParser(description="Analyze a legal document with AI.")
    parser.add_argument("filepath", type=str, help="Path to the document (txt/pdf)")
    parser.add_argument("--language", type=str, default="English", help="Document language (default=English)")
    args = parser.parse_args()

    # Load document
    if args.filepath.lower().endswith(".pdf"):
        document_text = read_pdf_text(args.filepath)
    else:
        document_text = read_text_file(args.filepath)

    if not document_text.strip():
        console.print(Panel("❌ Could not read document content", border_style="red", box=ROUNDED))
        return

    console.print(Panel(f"✅ Document '[bold]{args.filepath}[/bold]' loaded successfully.\n🌐 Language: [bold cyan]{args.language}[/bold cyan]", border_style="green", box=ROUNDED))

    # Start menu loop
    menu_loop(document_text, args.language)


if __name__ == "__main__":
    main()
