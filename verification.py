#This module makes sure that the password meets the requirements
from password_strength import PasswordPolicy

policy = PasswordPolicy.from_names(min_length=6, uppercase=1, numbers=1, special=1)

def check_password_strength(password):
    """
    Checks if password meets the minimum strength criteria.
    """
    if len(policy.test(password)) > 0:
        return False
    return True
