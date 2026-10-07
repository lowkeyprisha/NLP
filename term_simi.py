from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

documents = []

n = int(input("Enter number of documents: "))

for i in range(n):
    documents.append(input(f"Enter document {i+1}: "))

vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix = vectorizer.fit_transform(documents)

terms = vectorizer.get_feature_names_out()

term_matrix = tfidf_matrix.T

similarity_matrix = cosine_similarity(term_matrix)

print("\nTerms after stop-word removal:")
print(terms)

print("\nTerm Similarity Matrix:")
print(similarity_matrix)

print("\nPairwise Term Similarity:")

for i in range(len(terms)):
    for j in range(i + 1, len(terms)):
        print(f"{terms[i]} & {terms[j]}: {similarity_matrix[i][j]:.2f}")