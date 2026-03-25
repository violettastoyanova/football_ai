import re

def detect_intent(text):
    text = text.strip()
    lower = text.lower()

    # exit
    if lower == "изход":
        return "exit", {}

    # help
    if lower == "помощ":
        return "help", {}

    # transfer
    match = re.search(
        r"^трансфер\s+(.+?)\s+от\s+(.+?)\s+в\s+(.+?)\s+(\d{2}-\d{2}-\d{4})$",
        text,
        re.IGNORECASE
    )
    if match:
        return "transfer_player", {
            "player": match.group(1),
            "from_club": match.group(2),
            "to_club": match.group(3),
            "date": match.group(4)
        }

    # show transfers player
    match = re.search(r"^покажи трансфери на\s+(.+)$", text, re.IGNORECASE)
    if match:
        return "show_transfers_player", {"name": match.group(1)}

    # show transfers club
    match = re.search(r"^покажи трансфери на клуб\s+(.+)$", text, re.IGNORECASE)
    if match:
        return "show_transfers_club", {"club": match.group(1)}

    return "unknown", {}