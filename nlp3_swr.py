import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

text = input("Enter your text: \n")

stop_words = set(stopwords.words('english'))

words = text.split()

filtered_words = [
    word for word in words
    if word.lower() not in stop_words
]
print("\n\n\n")
print("After stop-word removal:\n", " ".join(filtered_words))

