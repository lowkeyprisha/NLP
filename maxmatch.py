import re

text = input("Enter a sentence: ")

tokens = re.findall(r'\w+', text)

print(tokens)