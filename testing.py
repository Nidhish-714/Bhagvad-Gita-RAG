import pandas as pd
from support import create_hybrid_searcher

def evaluate_rag_accuracy(csv_path):
    """
    Evaluate RAG pipeline accuracy based on first retrieved result for all questions.
    
    Args:
        csv_path: Path to the CSV file containing questions
    """
    # Load the dataset
    df = pd.read_csv(csv_path)
    
    # Create unique identifier for each verse
    df['verse_id'] = df['chapter'].astype(str) + '_' + df['verse'].astype(str)
    
    # Split questions into individual questions
    df_expanded = df.copy()
    df_expanded['questions'] = df_expanded['questions'].fillna('')
    df_expanded = df_expanded.assign(questions=df_expanded['questions'].str.split(',')).explode('questions')
    
    # Clean questions
    df_expanded = df_expanded[df_expanded['questions'].str.strip() != '']
    df_expanded['questions'] = df_expanded['questions'].str.strip()
    
    # Initialize the hybrid searcher
    hybrid_searcher = create_hybrid_searcher()
    
    # Initialize counters
    correct_retrievals = 0
    total_questions = 0
    results = []
    
    print("Starting evaluation...")
    
    # Evaluate each question
    for idx, row in df_expanded.iterrows():
        question = row['questions']
        true_chapter = row['chapter']
        true_verse = row['verse']
        true_verse_id = row['verse_id']
        
        # Get only top-1 prediction for each question
        search_results = hybrid_searcher.search(question, top_k=1, alpha=0.6)
        
        if search_results:
            # Get the first result
            top_result = search_results[0]
            pred_chapter = top_result.get('chapter')
            pred_verse = top_result.get('verse')
            pred_verse_id = f"{pred_chapter}_{pred_verse}"
            
            # Check if prediction matches ground truth
            is_correct = pred_verse_id == true_verse_id
            
            if is_correct:
                correct_retrievals += 1
            
            # Store result details
            results.append({
                'question': question,
                'true_chapter': true_chapter,
                'true_verse': true_verse,
                'predicted_chapter': pred_chapter,
                'predicted_verse': pred_verse,
                'is_correct': is_correct,
                'confidence_score': top_result.get('score', 0)
            })
        
        total_questions += 1
        
        # Print progress every 100 questions
        if total_questions % 100 == 0:
            current_accuracy = (correct_retrievals / total_questions) * 100
            print(f"Processed {total_questions} questions... Current accuracy: {current_accuracy:.2f}%")
    
    # Calculate final accuracy
    final_accuracy = (correct_retrievals / total_questions) * 100
    
    # Create results DataFrame
    results_df = pd.DataFrame(results)
    
    # Print final results
    print("\n=== Final Evaluation Results ===")
    print(f"Total questions evaluated: {total_questions}")
    print(f"Correct retrievals: {correct_retrievals}")
    print(f"Final accuracy: {final_accuracy:.2f}%")
    
    # Print example correct and incorrect retrievals
    print("\n=== Example Correct Retrievals ===")
    correct_samples = results_df[results_df['is_correct']].sample(min(3, len(results_df[results_df['is_correct']])))
    for _, result in correct_samples.iterrows():
        print(f"\nQuestion: {result['question']}")
        print(f"True: Chapter {result['true_chapter']}, Verse {result['true_verse']}")
        print(f"Predicted: Chapter {result['predicted_chapter']}, Verse {result['predicted_verse']}")
        print(f"Confidence Score: {result['confidence_score']:.4f}")
    
    print("\n=== Example Incorrect Retrievals ===")
    incorrect_samples = results_df[~results_df['is_correct']].sample(min(3, len(results_df[~results_df['is_correct']])))
    for _, result in incorrect_samples.iterrows():
        print(f"\nQuestion: {result['question']}")
        print(f"True: Chapter {result['true_chapter']}, Verse {result['true_verse']}")
        print(f"Predicted: Chapter {result['predicted_chapter']}, Verse {result['predicted_verse']}")
        print(f"Confidence Score: {result['confidence_score']:.4f}")
    
    # Save results
    results_df.to_csv('rag_evaluation_results.csv', index=False)
    
    return {
        'accuracy': final_accuracy,
        'total_questions': total_questions,
        'correct_retrievals': correct_retrievals,
        'detailed_results': results_df
    }

if __name__ == "__main__":
    # Path to your CSV file
    csv_path = "Bhagwad_Gita_Verses_English_Questions.csv"
    
    # Run evaluation
    results = evaluate_rag_accuracy(csv_path)