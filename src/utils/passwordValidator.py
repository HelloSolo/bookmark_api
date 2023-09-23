def validate(password):
    if len(password) < 6:
        return "Password is too short"
    else:
        return True
