from services.transfers_service import (
    transfer_player,
    list_transfers_by_player,
    list_transfers_by_club
)


def handle_intent(intent, params):
    if intent == "transfer_player":
        return transfer_player(
            params["player"],
            params["from_club"],
            params["to_club"],
            params["date"]
        )

    if intent == "show_transfers_player":
        return list_transfers_by_player(params["name"])

    if intent == "show_transfers_club":
        return list_transfers_by_club(params["club"])

    return "Невалидна команда."