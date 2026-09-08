import re
def regex_tokenize(text):
    tokens = re.findall(r'\w+|[^\w\s]', text)
    return tokens
text = input("Enter a sentence: ")
tokens = regex_tokenize(text)
print("\nOriginal Text:")
print(text)
print("\nRegex Tokenized Output:")
for token in tokens:
    print(token)












