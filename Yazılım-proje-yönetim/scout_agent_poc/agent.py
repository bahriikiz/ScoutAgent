import re


import re

def parse_instruction(text: str, default_freq_hours: float = 24.0) -> dict:
    """
    Doğal dilden saat ve dakika destekli aralıkları parse eder.
    """
    # Find URL
    url_match = re.search(r"(https?://\S+)", text)
    if not url_match:
        raise ValueError("No URL found in instruction. Include a full 'http...' URL.")
    url = url_match.group(1)

    # Find frequency (e.g., 'every 4 hours 15 minutes', 'every 90 minutes')
    freq_match = re.search(
        r"every\s+((?P<hours>\d+(?:\.\d+)?)\s*(?:hours?|hrs?)\s*)?((?P<minutes>\d+(?:\.\d+)?)\s*minutes?)?",
        text, re.IGNORECASE
    )

    if freq_match:
        hours = float(freq_match.group("hours") or 0)
        minutes = float(freq_match.group("minutes") or 0)
        frequency_hours = hours + minutes / 60
        if frequency_hours == 0:
            print(f"⚠️ No valid time found; defaulting to {default_freq_hours} hours.")
            frequency_hours = default_freq_hours
    else:
        print(f"⚠️ No frequency found; defaulting to {default_freq_hours} hours.")
        frequency_hours = default_freq_hours

    # Task prompt:
    if freq_match:
        prompt_start = freq_match.end()
        remainder = text[prompt_start:].strip()
    else:
        remainder = text[url_match.end():].strip()
    task_prompt = re.sub(r"^[,;:\-\.\s]+", "", remainder)
    if not task_prompt:
        task_prompt = f"Monitor changes at {url}"

    return {"url": url, "frequency": frequency_hours, "task_prompt": task_prompt}



def confirm_task(details: dict) -> bool:
    """
    Displays parsed details and prompts user for confirmation.
    Returns True if confirmed, False otherwise.
    """
    print("\nParsed Task Details:")
    print(f"  URL        : {details['url']}")
    print(f"  Frequency  : {details['frequency']} hours")
    print(f"  Task Prompt: {details['task_prompt']}")

    choice = input("Confirm task? (y/n): ")
    return choice.strip().lower().startswith("y")


if __name__ == "__main__":
    print("=== Scout Agent Task Ingestion (Regex Parser) ===")
    user_text = input("Enter instruction: ")
    try:
        parsed = parse_instruction(user_text)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

    if confirm_task(parsed):
        print("Task confirmed. Next: save to DB.")
    else:
        print("Task cancelled.")
