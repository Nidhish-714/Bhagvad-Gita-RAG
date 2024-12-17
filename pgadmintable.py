import pandas as pd
import json
from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Database connection details (replace with your own)
DB_USER = "postgres"
DB_PASSWORD = "nio"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "csv_with_embeddings"

# PostgreSQL table name
TABLE_NAME = "verses_with_embeddings"

# Define a SQLAlchemy base model
Base = declarative_base()

class Verse(Base):
    __tablename__ = "verses_with_embeddings"
    
    id = Column(Integer, primary_key=True)
    verse_number = Column(String, nullable=False)
    verse_in_sanskrit = Column(Text, nullable=False)
    sanskrit_verse_transliteration = Column(Text, nullable=False)
    translation_in_english = Column(Text, nullable=False)
    fullplot = Column(Text, nullable=False)
    translation_in_hindi = Column(Text, nullable=False)
    meaning_in_hindi = Column(Text, nullable=False)
    embedding = Column(Text, nullable=False)  # Store embedding as JSON

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
        embeddings.append(json.dumps(embedding))  # Convert list to JSON string

    df['embedding'] = embeddings

    # Save the updated CSV
    output_path = "output_with_embeddings.csv"
    # df.to_csv(output_path, index=False)
    print(f"Updated CSV saved to {output_path}")

    return df

def create_postgres_table(df, batch_size=1000):
    # Create the database engine
    engine_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(engine_url)

    # Create the table (this will create the table based on the model defined)
    Base.metadata.create_all(engine)

    # Insert data into the table
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Loop through the dataframe in batches
        for start in range(0, len(df), batch_size):
            end = min(start + batch_size, len(df))
            batch = df.iloc[start:end]
            records = []
            
            for _, row in batch.iterrows():
                record = Verse(
                    verse_number=row['verse_number'],
                    verse_in_sanskrit=row['verse_in_sanskrit'],
                    sanskrit_verse_transliteration=row['sanskrit_verse_transliteration'],
                    translation_in_english=row['translation_in_english'],
                    fullplot=row['fullplot'],
                    translation_in_hindi=row['translation_in_hindi'],
                    meaning_in_hindi=row['meaning_in_hindi'],
                    embedding=row['embedding']  # Assuming embedding is in the correct format
                )
                records.append(record)

            # Add the batch to the session and commit
            session.bulk_save_objects(records)
            session.commit()

        print(f"Data successfully inserted into the '{TABLE_NAME}' table.")
    
    except Exception as e:
        session.rollback()
        print(f"Error inserting data: {e}")
    
    finally:
        session.close()



if __name__ == "__main__":
    input_csv = "bhagavad_gita.csv"  # Replace with your CSV file path

    # Load the MiniLM model
    model_name = "all-MiniLM-L6-v2"
    model = SentenceTransformer(model_name)

    df = process_csv(input_csv, model)
    create_postgres_table(df)
