# adminpanel/logic/password.py
#
# WHAT: Custom teaching-oriented password hashing and verification module.
#
# IMPORTANT LIMITATION & ACADEMIC CONTEXT:
# This algorithm is built strictly for TEACHING AND COLLEGE PROJECT DEMONSTRATION purposes.
# It demonstrates the foundational concepts of hashing:
# - One-way transformation using modular arithmetic and XOR bitwise operations
# - Salting to defend against precomputed dictionary/rainbow table attacks
# - Fixed-length digest formatting
#
# SECURITY NOTICE:
# This is NOT a production-grade cryptographic algorithm. It does NOT offer the cryptographic
# collision resistance, key-stretching, or brute-force resistance provided by established
# industry standards such as bcrypt, Argon2, PBKDF2, or SHA-256.
# It is designed specifically to fulfill the college requirement of writing our own manual
# application logic rather than using ready-made authentication libraries.

import secrets


def generate_salt() -> str:
    """
    Generates a cryptographically random salt using Python's standard-library `secrets` module.

    Why secrets?
    `secrets` is part of Python's standard library (no external pip package needed).
    It accesses the operating system's CSPRNG (Cryptographically Secure Pseudo-Random Number Generator).

    `secrets.token_hex(32)` produces 32 random bytes converted into a 64-character hexadecimal string.
    This salt ensures that two identical passwords will result in completely different hashes.
    """
    return secrets.token_hex(32)


def hash_password(password: str, salt: str) -> str:
    """
    Our custom teaching-oriented password processing algorithm.

    Algorithm Mechanism:
    1. Initializes four 32-bit state variables (values) with seed constants.
    2. Combines the plaintext password with the 64-character random salt:
       combined = password + salt
    3. Loops through each character in the combined string:
       - Obtains the Unicode integer code point: code = ord(combined[index])
       - Determines which slot (0 to 3) to update: slot = index % 4
       - Applies bitwise XOR (^) with the character code
       - Multiplies by the FNV prime constant (16777619)
       - Constrains the result to 32 bits using modulo 2^32 (4294967296)
    4. Formats each of the 4 state values as an 8-character zero-padded hexadecimal string (32 hex characters total).
    5. Expands and slices the resulting string to output a uniform 64-character hexadecimal hash.
    """
    values = [
        2166136261,
        16777619,
        2246822519,
        3266489917
    ]

    combined = password + salt

    index = 0

    while index < len(combined):
        code = ord(combined[index])
        slot = index % 4

        values[slot] = (values[slot] ^ code) * 16777619
        values[slot] = values[slot] % 4294967296

        index += 1

    result = ''

    for value in values:
        result += format(value, '08x')

    while len(result) < 64:
        result += result

    return result[:64]


def verify_password(entered_password: str, stored_salt: str, stored_password_hash: str) -> bool:
    """
    Verifies an entered password during login against the stored credentials in MySQL.

    Algorithm:
    1. Receives the entered plaintext password, the stored salt, and the stored hash.
    2. Runs our own hash_password(entered_password, stored_salt) using the exact same salt.
    3. Compares the newly generated hash with the stored password_hash.
    4. Returns True if they match, False otherwise.

    Note: The plaintext password is NEVER compared directly or stored in the database.
    """
    if not entered_password or not stored_salt or not stored_password_hash:
        return False

    generated_hash = hash_password(entered_password, stored_salt)

    return generated_hash == stored_password_hash
