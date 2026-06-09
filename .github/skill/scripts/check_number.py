"""
check_number.py — Reference script for Hello World skill
Handles conditional logic: checks if a number is odd or even
and returns an appropriate message/response.
"""

def check_odd_even(number):
    """
    Check if a number is odd or even.
    Returns a dict with:
        - result: 'odd' or 'even'
        - message: a friendly response message
        - emoji: a fun emoji to go with the message
    """
    try:
        num = int(number)
    except (ValueError, TypeError):
        return {
            "result": "invalid",
            "message": f"'{number}' doesn't look like a number to me! Try entering a whole number.",
            "emoji": "🤔"
        }

    if num == 0:
        return {
            "result": "zero",
            "message": "Zero is neither odd nor even — it's in a class of its own!",
            "emoji": "🌀"
        }
    elif num % 2 == 0:
        return {
            "result": "even",
            "message": f"{num} is an EVEN number. Balanced and symmetric!",
            "emoji": "✅"
        }
    else:
        return {
            "result": "odd",
            "message": f"{num} is an ODD number. Unique and standing alone!",
            "emoji": "⚡"
        }


def get_response_message(number):
    """
    Main entry point. Returns a formatted response string
    that Claude can display directly to the user.
    """
    result = check_odd_even(number)
    return f"{result['emoji']} {result['message']}"


# --- Conditional branching example ---
# This shows how to extend the script with custom conditions.

def extended_check(number):
    """
    Extended conditional logic:
    - Is it odd or even?
    - Is it positive, negative, or zero?
    - Is it a prime number?
    Returns a full summary message.
    """
    try:
        num = int(number)
    except (ValueError, TypeError):
        return "⚠️ Invalid input. Please provide a whole number."

    messages = []

    # Condition 1: Sign
    if num > 0:
        messages.append("➕ Positive")
    elif num < 0:
        messages.append("➖ Negative")
    else:
        messages.append("🌀 Zero")

    # Condition 2: Odd or Even (skip for zero)
    if num != 0:
        if num % 2 == 0:
            messages.append("✅ Even")
        else:
            messages.append("⚡ Odd")

    # Condition 3: Prime check (for positive numbers > 1)
    if num > 1:
        is_prime = all(num % i != 0 for i in range(2, int(num**0.5) + 1))
        if is_prime:
            messages.append("🌟 Prime")
        else:
            messages.append("🔢 Not Prime")

    return f"Number {num}: " + " | ".join(messages)


# --- Run directly for quick testing ---
if __name__ == "__main__":
    test_numbers = [0, 1, 2, 7, 12, 13, -4, -7, "abc"]
    print("=== Basic Odd/Even Check ===")
    for n in test_numbers:
        print(f"  Input: {n!r:>6}  →  {get_response_message(n)}")

    print("\n=== Extended Conditional Check ===")
    for n in test_numbers:
        print(f"  {extended_check(n)}")
