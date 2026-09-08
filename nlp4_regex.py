import re
text = input("Enter your text: ")
pattern = re.compile(
    r"(?P<EMAIL>[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})"
    r"|(?P<URL>(?:https?://|www\.)[^\s]+)"
    r"|(?P<PHONE>(?:\+91[\s-]?)?[6-9]\d{4}[\s-]?\d{5})"
    r"|(?P<MONEY>(?:₹|\$|€|£)\s?\d[\d,]*(?:\.\d{1,2})?)"
    r"|(?P<DATE>\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
    r"|(?P<PERCENTAGE>\d+(?:\.\d+)?%)"
    r"|(?P<TITLE>\b(?:Mr|Mrs|Ms|Miss|Dr|Prof)\.?)"
    r"|(?P<HASHTAG>#\w+)"
    r"|(?P<MENTION>@\w+)"
    r"|(?P<NUMBER>\d+(?:\.\d+)?)"
    r"|(?P<WORD>[A-Za-z]+(?:['-][A-Za-z]+)*)"
    r"|(?P<PUNCTUATION>[.,!?;:])"
    r"|(?P<SYMBOL>[^\w\s])"
    r"|(?P<VOWEL>\b[A-Za-z]*[aeiouAEIOU][A-Za-z]*\b)",
    re.IGNORECASE
)
print("\n--- TOKENS ---")
for match in pattern.finditer(text):
    print(match.group(), "->", match.lastgroup)