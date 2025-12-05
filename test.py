import questionary

should_proceed = questionary.confirm("Are you gay?", default=False).ask()