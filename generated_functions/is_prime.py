def is_prime(n: int) -> bool:
    """
    Check if a number is prime.
    
    :param n: Integer to check for primality.
    :return: True if n is prime, else False.
    """
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True