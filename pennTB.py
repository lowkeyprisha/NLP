from nltk.tokenize import TreebankWordTokenizer

text = input("Enter a sentence: ")

tokenizer = TreebankWordTokenizer()
tokens = tokenizer.tokenize(text)

print(tokens)