from services.leagues_service import (
    create_league,
    add_team_to_league,
    remove_team_from_league,
    show_league_teams,
    generate_schedule,
    delete_schedule,
    display_full_schedule
)


def handle_intent(intent, params):
    # Лиги
    if intent == "create_league":
        return create_league(params["name"], params["season"])

    if intent == "add_team_to_league":
        return add_team_to_league(params["club"], params["league_name"], params["season"])

    if intent == "remove_team_from_league":
        return remove_team_from_league(params["club"], params["league_name"], params["season"])

    if intent == "show_league_teams":
        return show_league_teams(params["league_name"], params["season"])

    if intent == "generate_schedule":
        return generate_schedule(params["league_name"], params["season"])

    if intent == "delete_schedule":
        return delete_schedule(params["league_name"], params["season"])

    if intent == "show_schedule":
        return display_full_schedule(params["league_name"], params["season"])

    # Съществуващите ти intents (transfer_player и т.н.)
    # ...

    return "Невалидна команда."