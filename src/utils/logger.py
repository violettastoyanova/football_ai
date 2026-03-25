from datetime import datetime

def log_command(text, intent, result):
    with open("commands.log", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | {text} | {intent} | {result}\n")