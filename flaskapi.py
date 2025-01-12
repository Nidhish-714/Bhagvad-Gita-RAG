from bson import ObjectId
from flask import Flask, request, jsonify
from support import create_hybrid_searcher
import nltk
import logging
from flask_cors import CORS

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
        # print(data)
        if not data or 'query' not in data:
            return jsonify({"error": "No query provided"}), 400

        query = data['query']
        top_k = data.get('top_k', 5)  # Default to 5 if not provided
        alpha = data.get('alpha', 0.6)  # Default to 0.6 if not provided

        # Perform the search
        results = hybrid_searcher.search(query, top_k=top_k, alpha=alpha)

        # Format the results
        formatted_results = []
        print(results)
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
            "results": formatted_results
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