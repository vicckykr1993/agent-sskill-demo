---
name: hello world
description: Responds when the user says "hello world", "hi world", or "hey world" with ASCII art and a welcome message. Also handles conditional number checking — use this skill whenever the user greets with hello/hi/hey world OR asks to check if a number is odd or even.
---

# Hello World Skill

## Triggers
This skill activates when the user:
1. Says **"hello world"**, **"hi world"**, or **"hey world"**
2. Asks to **check if a number is odd or even** after the greeting

---

## Step 1 — Greet with ASCII Art

When triggered by a hello/hi/hey world greeting, respond with large ASCII art followed by a welcome message.

```
 _   _      _ _        __        __         _     _ 
| | | | ___| | | ___   \ \      / /__  _ __| | __| |
| |_| |/ _ \ | |/ _ \   \ \ /\ / / _ \| '__| |/ _` |
|  _  |  __/ | | (_) |   \ V  V / (_) | |  | | (_| |
|_| |_|\___|_|_|\___/     \_/\_/ \___/|_|  |_|\__,_|
```

Always try to make the ASCII art **bigger and bolder** than the example above.

After the art, add a short friendly message like:
> "Welcome, Viccky! 🚀 Type a number and I'll tell you if it's odd or even!"

---

## Step 2 — Conditional Number Check

After greeting the user, prompt them to enter a number. Then apply the following conditional logic:

### How to check (reference: `scripts/check_number.py`)

Use the logic from `scripts/check_number.py` to determine the response. The script has two modes:

#### Basic Check (`get_response_message`)
| Condition       | Response                                      |
|----------------|-----------------------------------------------|
| Input is 0      | 🌀 Zero is neither odd nor even               |
| Number is even  | ✅ `{n}` is an EVEN number. Balanced!         |
| Number is odd   | ⚡ `{n}` is an ODD number. Unique!            |
| Invalid input   | 🤔 Prompt the user to enter a valid number    |

#### Extended Check (`extended_check`)
Runs three conditions in sequence:
1. **Sign** — Is the number positive, negative, or zero?
2. **Parity** — Is it odd or even?
3. **Primality** — Is it a prime number? (only for positive numbers > 1)

Returns all results combined in one line, e.g.:
> `Number 7: ➕ Positive | ⚡ Odd | 🌟 Prime`

---

## Step 3 — Ask to Continue

After showing the result, ask:
> "Want to check another number? Or type 'hello world' again to restart! 😊"

---

## Reference Script

See `scripts/check_number.py` for the full conditional logic implementation.

Run it directly to test:
```bash
python scripts/check_number.py
```

To use a specific function in your code:
```python
from scripts.check_number import get_response_message, extended_check

print(get_response_message(7))       # Basic: odd/even
print(extended_check(13))            # Extended: sign + parity + prime
```

---

## Example Interaction

**User:** hello world
**Claude:** [ASCII art] Welcome, Viccky! 🚀 Type a number and I'll tell you if it's odd or even!

**User:** 13
**Claude:** ⚡ 13 is an ODD number. Unique and standing alone!
*(Extended: ➕ Positive | ⚡ Odd | 🌟 Prime)*
Want to check another number?

**User:** abc
**Claude:** 🤔 'abc' doesn't look like a number to me! Try entering a whole number.
