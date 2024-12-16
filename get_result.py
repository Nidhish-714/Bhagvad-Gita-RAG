from sentence_transformers import SentenceTransformer, util
from bson.objectid import ObjectId
from pymongo.mongo_client import MongoClient

uri = "mongodb://nidhish:1234@nrsc-bot-shard-00-00.h0weh.mongodb.net:27017,nrsc-bot-shard-00-01.h0weh.mongodb.net:27017,nrsc-bot-shard-00-02.h0weh.mongodb.net:27017/?ssl=true&replicaSet=atlas-p4ysqw-shard-0&authSource=admin&retryWrites=true&w=majority&appName=NRSC-BOT"

# Create a new client and connect to the server
client = MongoClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db=client["mytestdb"]
     

collection=db["collection"]
# Load the embedding model
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Perform similarity search and return the ID of the most similar document
def get_most_similar_document_id(query):
    # Encode the query into an embedding
    query_embedding = embedding_model.encode(query)

    # Retrieve all documents from the collection
    documents = list(collection.find({}, {"_id": 1, "fullplot": 1}))

    # Compute similarities and find the most similar document
    most_similar = None
    highest_similarity = -1
    for doc in documents:
        if 'fullplot' in doc:
            doc_embedding = embedding_model.encode(doc['fullplot'])
            similarity = util.cos_sim(query_embedding, doc_embedding).item()
            if similarity > highest_similarity:
                highest_similarity = similarity
                most_similar = doc["_id"]

    # Return the ID of the most similar document
    return most_similar

# Example usage
query = "The two armies had gathered on the battlefield of Kurukshetra"
most_similar_id = get_most_similar_document_id(query)

if most_similar_id:
    print(f"The ID of the most similar document is: {most_similar_id}")
    # Fetch and print the entire document
    document = collection.find_one({"_id": ObjectId(most_similar_id)})
    if document:
        print("Document found:")
        print(document)
else:
    print("No similar document found.")
