from support import create_hybrid_searcher

import nltk
nltk.download('punkt_tab')

# Create the hybrid searcher instance
hybrid_searcher = create_hybrid_searcher()

# Perform the query
query = "When does Yoga commence? When should I start doing Yoga?"
results = hybrid_searcher.search(query, top_k=1, alpha=0.6)


# Extract the first result and save its 'translation' and 'fullplot' into document_text
if results:
    first_result = results[0]  # Assuming we want the first result
    translation = first_result.get('translation', '')  # Extract translation, default to empty string if not present
    fullplot = first_result.get('fullplot', '')  # Extract fullplot, default to empty string if not present

    # Combine them into document_text
    document_text = f"Translation: {translation}\nFull Plot: {fullplot}"
else:
    document_text = "No results found."



# from groq import Groq

# client = Groq(
#     api_key="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",
# )

# document_text = results[0].sanskrit
# chat_completion = client.chat.completions.create(
#                 messages=[
#                     {"role": "system", "content": "You are a helpful assistant."},
#                     {"role": "user", "content": document_text}
#                 ],
#                 model="llama-3.1-70b-versatile",
#             )
# summary = chat_completion.choices[0].message.content
# print(summary)


# Print results
# for result in results:
#     print(f"Score: {result['score']}")
#     print("Document:")
#     for key, value in result.items():
#         print(f"{key}: {value}")
#     print("---")
