from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import numpy as np
from rank_bm25 import BM25Okapi
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
from bson.objectid import ObjectId

class HybridSearch:
    def __init__(self, mongo_uri, pinecone_instance, model_name='all-MiniLM-L6-v2'):
        # Initialize MongoDB connection
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client['mytestdb']
        self.collection = self.db['collection']
        
        # Initialize Pinecone
        self.pinecone_index = pinecone_instance
        
        # Initialize sentence transformer model
        self.model = SentenceTransformer(model_name)
        
        # Download required NLTK data
        nltk.download('punkt')
        nltk.download('stopwords')
        self.stop_words = set(stopwords.words('english'))

    def preprocess_text(self, text):
        # Convert to lowercase and remove special characters
        text = re.sub(r'[^\w\s]', '', text.lower())
        # Tokenize
        tokens = word_tokenize(text)
        # Remove stopwords
        tokens = [token for token in tokens if token not in self.stop_words]
        return tokens

    def create_vector_embeddings(self):
        """Create and store vector embeddings for all documents in Pinecone"""
        documents = self.collection.find({}, {'_id': 1, 'fullplot': 1})
        
        for doc in documents:
            if 'fullplot' in doc and doc['fullplot']:
                # Generate embedding
                embedding = self.model.encode(doc['fullplot']).tolist()
                
                # Store in Pinecone with MongoDB _id as metadata
                self.pinecone_index.upsert(
                    vectors=[{
                        'id': str(doc['_id']),
                        'values': embedding,
                        'metadata': {'mongo_id': str(doc['_id'])}
                    }]
                )

    def hybrid_search(self, query, top_k=5, alpha=0.5):
        """
        Perform hybrid search using both sparse and dense retrieval
        alpha: weight for combining scores (0-1), higher value gives more weight to dense retrieval
        """
        # Generate query embedding for dense retrieval
        query_embedding = self.model.encode(query).tolist()
        
        # Perform dense retrieval using Pinecone
        dense_results = self.pinecone_index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )

        # Perform sparse retrieval using BM25
        # First, get all documents
        documents = list(self.collection.find({}, {'_id': 1, 'fullplot': 1}))
        
        # Preprocess documents for BM25
        processed_docs = [self.preprocess_text(doc['fullplot']) for doc in documents if 'fullplot' in doc]
        bm25 = BM25Okapi(processed_docs)
        
        # Get BM25 scores
        processed_query = self.preprocess_text(query)
        bm25_scores = bm25.get_scores(processed_query)
        
        # Normalize BM25 scores
        bm25_scores = (bm25_scores - np.min(bm25_scores)) / (np.max(bm25_scores) - np.min(bm25_scores))
        
        # Create a dictionary of dense scores
        dense_scores = {
            match.metadata['mongo_id']: match.score 
            for match in dense_results.matches
        }
        
        # Combine scores
        final_scores = []
        for i, doc in enumerate(documents):
            doc_id = str(doc['_id'])
            dense_score = dense_scores.get(doc_id, 0)
            sparse_score = bm25_scores[i]
            
            # Combine scores using weighted average
            combined_score = (alpha * dense_score) + ((1 - alpha) * sparse_score)
            final_scores.append((doc, combined_score))
        
        # Sort by combined score and return top_k results
        final_results = sorted(final_scores, key=lambda x: x[1], reverse=True)[:top_k]
        
        return final_results

        

    def search(self, query, top_k=5, alpha=0.5):
        """Wrapper method for performing search and returning formatted results"""
        # Perform hybrid search to get initial matches with their scores
        hybrid_results = self.hybrid_search(query, top_k, alpha)
        
        mylist = []
        for doc, score in hybrid_results:
            # Retrieve the full document from MongoDB using its ObjectId
            complete_doc = self.collection.find_one({"_id": ObjectId(doc['_id'])})
            if complete_doc:
                # Add the score to the complete document
                complete_doc['score'] = score
                mylist.append(complete_doc)

        # Print formatted results
        for result in mylist:
            print(f"_id: {result['_id']}")
            print(f"chapter: {result.get('chapter', 'N/A')}")
            print(f"verse: {result.get('verse', 'N/A')}")
            print(f"speaker: {result.get('speaker', 'N/A')}")
            print(f"sanskrit: {result.get('sanskrit', 'N/A')}")
            print(f"translation: {result.get('translation', 'N/A')}")
            # print(f"questions: {result.get('questions', 'N/A')}")
            print(f"fullplot: {result.get('fullplot', 'N/A')}")
            print("=" * 50)

        return mylist


def create_hybrid_searcher():
    mongo_uri = "mongodb+srv://nidhish:nidhish@cluster1.vthss.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1"
    from pinecone import Pinecone
    pc = Pinecone(api_key="pcsk_7Cj4Kj_bK4WbhEpxCM4PJQWLkP8muKcU6eRAN7pSLy2fphFvVr9NXuYY395kHhKo3K6za")
    index = pc.Index(host="https://mydb-j1b0j8k.svc.aped-4627-b74a.pinecone.io")
    hybrid_searcher = HybridSearch(mongo_uri, index)
    return hybrid_searcher