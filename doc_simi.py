from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

documents = []

n = int(input("Enter number of documents: "))

for i in range(n):
    text = input(f"Enter document {i+1}: ")
    documents.append(text)

vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(documents)

terms = vectorizer.get_feature_names_out()

print("\nDocument-Term Matrix:")
print("\t" + "\t".join(terms))

for i in range(n):
    print(f"Doc{i+1}\t" + "\t".join(f"{x:.2f}" for x in tfidf_matrix[i].toarray()[0]))

similarity_matrix = cosine_similarity(tfidf_matrix)

print("\nDocument Similarity Matrix:")
print(similarity_matrix)

print("\nPairwise Similarity:")
for i in range(n):
    for j in range(i + 1, n):
        print(f"Document {i+1} & Document {j+1}: {similarity_matrix[i][j]:.2f}")