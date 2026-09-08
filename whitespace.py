import nltk
def whitespace_tokenize(text):
    tokens = text.split()
    return tokens
text = input("Enter a sentence: ")
tokens = whitespace_tokenize(text)
print("\nOriginal Text:")
print(text)
print("\nWhitespace Tokenized Output:")
for token in tokens:
    print(token)




