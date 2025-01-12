# Bhagavad Gita RAG System

A Retrieval-Augmented Generation (RAG) system for querying and understanding the Bhagavad Gita using hybrid search (combining dense and sparse retrieval methods).

## Current Accuracy is 98.4%

## Setup Instructions

### 1. Create and Activate Virtual Environment

```bash
# Create a new virtual environment
python -m venv myenv

# Activate the virtual environment
# For Windows:
myenv\Scripts\activate
# For Unix or MacOS:
source myenv/bin/activate
```

### 2. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### 3. Data Preparation and Embeddings

The MongoDB Cluster is already ingested with data from the CSV files , make_embeddings file just creates and stores embeddings in the PineConeDB from the MongoDB documents.
Before running queries, you need to create embeddings for the verses:

```bash
# Generate embeddings
python make_embeddings.py
```

This step will:

- Process the Bhagavad Gita verses
- Create vector embeddings
- Store them in the vector database

## Usage

### Running Queries

To start querying the system:

```bash
# Run the main application
python app.py
```

You can then input your questions about the Bhagavad Gita, and the system will retrieve the most relevant verses.

# Running the Application

Start by running the flask server file flaskapi.py

```bash
# Run the main application
python flaskapi.py
```

Start the frontend by running the command

```bash
# Run the main application
cd frontend-maudifive
npm i
npm start
```


### Testing Accuracy

To evaluate the system's performance:

```bash
# Run the testing script
python testing.py
```

This will:

- Process all questions from the dataset
- Calculate retrieval accuracy
- Generate a detailed evaluation report
- Save results in `rag_evaluation_results.csv`

## File Structure

```
BHAGVAD-GITA-RAG/
├── __pycache__/
├── myenv/
├── .gitignore
├── app.py                                         # Main application file
├── bhagavad_gitaa.csv                            # Source verses data
├── Bhagwad_Gita_Verses_English_Questions.csv      # Questions dataset
├── final_search.ipynb                            # Search implementation notebook
├── make_embeddings.py                            # Embedding generation script
├── Patanjali_Yoga_Sutras_Verses_English_Questions.csv
├── rag_evaluation_results.csv                    # Testing results
├── readme.md                                     # This file
├── requirements.txt                              # Dependencies
├── search.ipynb                                  # Search development notebook
├── support.py                                    # Helper functions
└── testing.py                                    # Accuracy testing script
```

## Requirements

- Python 3.8+
- MongoDB
- Pinecone (for vector storage)
- Required Python packages (specified in requirements.txt)

## Notes

- Make sure MongoDB is running locally before starting the application
- Ensure you have proper API keys configured for Pinecone
- The system uses a hybrid search approach combining dense and sparse retrieval methods
- Testing results will be saved in `rag_evaluation_results.csv`

## Common Issues

If you encounter any issues:

1. Ensure all dependencies are installed correctly
2. Verify MongoDB is running
3. Check if embeddings were generated successfully
4. Ensure all required CSV files are in the correct location

For any additional issues, please check the error messages or create an issue in the repository.

## Current Accuracy is 98.4%
