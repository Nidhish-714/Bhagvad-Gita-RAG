from bson import ObjectId
from flask import Flask, request, jsonify
from support import create_hybrid_searcher
import nltk
import logging
from flask_cors import CORS

import os
from groq import Groq

client = Groq(
    api_key="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",
)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.download('punkt_tab')
except Exception as e:
    logger.error(f"Failed to download NLTK data: {str(e)}")

# Create the hybrid searcher instance
try:
    hybrid_searcher = create_hybrid_searcher()
    logger.info("Hybrid searcher initialized successfully")
except Exception as e:
    logger.error(f"Failed to create hybrid searcher: {str(e)}")
    hybrid_searcher = None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "searcher_status": hybrid_searcher is not None})

@app.route('/search', methods=['POST'])
def search():
    """
    Search endpoint that accepts POST requests with JSON data
    Expected format: {"query": "your search query", "top_k": 5, "alpha": 0.6}
    """
    if not hybrid_searcher:
        return jsonify({"error": "Searcher not initialized"}), 500

    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"error": "No query provided"}), 400

        query = data['query']
        top_k = data.get('top_k', 5)  # Default to 5 if not provided
        alpha = data.get('alpha', 0.6)  # Default to 0.6 if not provided

        # Perform the search
        results = hybrid_searcher.search(query, top_k=top_k, alpha=alpha)

        if results:
            first_result = results[0]  # Assuming we want the first result
            translation = first_result.get('translation', '')  # Extract translation, default to empty string if not present
            fullplot = first_result.get('fullplot', '')  # Extract fullplot, default to empty string if not present

            # Combine them into document_text
            document_text = f"Translation: {translation}\nFull Plot: {fullplot}"
        else:
            document_text = "No results found."
        if not results:
            return jsonify({"error": "No results found"}), 404

        

        if not document_text:
            return jsonify({"error": "First result does not contain content"}), 500

        # Use Groq to generate a summary
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": (
                        "You are an expert in ancient Sanskrit literature and philosophy. "
                        "Your task is to provide detailed and descriptive explanations for Sanskrit shlokas and verses. "
                        "Focus on the meaning, context, cultural significance, and practical application in daily life."
                    )},
                    {"role": "user", "content": (
                        "Below is a Sanskrit shloka or verse with its accompanying translation and description. "
                        "Please provide an in-depth explanation covering the following aspects:\n"
                        "- The meaning of the shloka in simple terms.\n"
                        "- The cultural or historical context of the verse.\n"
                        "- Any philosophical or spiritual significance.\n"
                        "- How it can be applied in modern life.\n\n"
                        f"{document_text}"
                    )}
                ],
                model="llama-3.1-70b-versatile",
            )
            summary = chat_completion.choices[0].message.content
            print(summary)
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            summary = "Error generating summary."

        # Format the results
        formatted_results = []
        for result in results:
            formatted_result = {
                'score': float(result['score']),  # Ensure score is serializable
                'document': {
                    k: (str(v) if isinstance(v, ObjectId) else v)  # Convert ObjectId to string
                    for k, v in result.items()
                    if k != 'score'
                }
            }
            formatted_results.append(formatted_result)


        return jsonify({
            "query": query,
            "results": formatted_results,
            "first_result_summary": summary
        })

    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
