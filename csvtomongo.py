import pandas as pd
import json
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient

# MongoDB connection details
MONGO_URI = "mongodb+srv://NishantLanjewar:nio2004@coephackathon.pbuvv.mongodb.net/?retryWrites=true&w=majority&appName=CoepHackathon"
DB_NAME = "csv_with_embeddings"
COLLECTION_NAME = "verses_with_embeddings"

def get_embedding(text, model):
    """Get vector embedding for a given text."""
    embedding = model.encode(text, normalize_embeddings=True).tolist()
    return embedding

def process_csv(file_path, model):
    # Read the CSV file
    df = pd.read_csv(file_path)

    # Ensure the 'fullplot' column exists
    if 'fullplot' not in df.columns:
        raise ValueError("The CSV file must contain a 'fullplot' column.")

    # Generate embeddings and add them as a new column
    embeddings = []
    for text in df['fullplot']:
        embedding = get_embedding(text, model)
        embeddings.append(embedding)  # Store as a list

    df['embedding'] = embeddings

    print("Embeddings added to the dataframe.")
    return df

def create_mongo_collection(df):
    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # Convert DataFrame to dictionary and insert into MongoDB
    try:
        records = df.to_dict(orient='records')  # Convert dataframe to list of dicts
        collection.insert_many(records)
        print(f"Data successfully inserted into the '{COLLECTION_NAME}' collection in MongoDB.")
    except Exception as e:
        print(f"Error inserting data into MongoDB: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    input_csv = "bhagavad_gita.csv"  # Replace with your CSV file path

    # Load the MiniLM model
    model_name = "all-MiniLM-L6-v2"
    model = SentenceTransformer(model_name)

    # Process CSV and generate embeddings
    df = process_csv(input_csv, model)

    # Insert into MongoDB
    create_mongo_collection(df)
