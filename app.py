from support import create_hybrid_searcher

import nltk
nltk.download('punkt_tab')

# Create the hybrid searcher instance
hybrid_searcher = create_hybrid_searcher()

# Perform the query
query = "When does Yoga commence? When should I start doing Yoga?"
results = hybrid_searcher.search(query, top_k=5, alpha=0.6)

# Print results
for result in results:
    print(f"Score: {result['score']}")
    print("Document:")
    for key, value in result.items():
        print(f"{key}: {value}")
    print("---")
