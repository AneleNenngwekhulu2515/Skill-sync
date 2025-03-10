from password_strength import PasswordPolicy

policy = PasswordPolicy.from_names(
        length= 6,
        uppercase = 1,
        numbers = 1,
        special = 1
)
        
def check_password_strength(password):
    """
    Checks if password meets the minimum strength criteria.
    """
    if len(policy.test(password)) > 0:
        return False
    return True
