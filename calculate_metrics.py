import os
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score

# CONFIGURATION
TEMPLATES_DIR = "Sign_Templates"
THRESHOLD = 0.15

def calculate_cosine_distance(v1, v2):
    """Calculate cosine distance between two vectors."""
    # Ensure they are normalized
    v1_norm = v1 / np.linalg.norm(v1) if np.linalg.norm(v1) > 0 else v1
    v2_norm = v2 / np.linalg.norm(v2) if np.linalg.norm(v2) > 0 else v2
    
    similarity = np.dot(v1_norm, v2_norm)
    return 1 - similarity

def run_validation():
    print("--- ISL-Similarity Studio: REAL METRICS CALCULATOR ---")
    
    # Check directory
    if not os.path.exists(TEMPLATES_DIR):
        print(f"Error: {TEMPLATES_DIR} folder not found. Run this script in the project root.")
        return

    # 1. Load all templates
    template_files = [f for f in os.listdir(TEMPLATES_DIR) if f.endswith('.npy')]
    if not template_files:
        print(f"Error: No .npy files found in {TEMPLATES_DIR}")
        return

    data = []
    labels = []
    
    for filename in template_files:
        label = filename.replace('.npy', '')
        filepath = os.path.join(TEMPLATES_DIR, filename)
        try:
            vector = np.load(filepath)
            data.append(vector)
            labels.append(label)
        except Exception as e:
            print(f"Error loading {filename}: {e}")

    num_samples = len(data)
    print(f"Loaded {num_samples} sign templates.")
    
    y_true = []
    y_pred = []
    
    # 2. Leave-One-Out Validation
    print("\nCalculating metrics (Leave-One-Out)...")
    for i in range(num_samples):
        query_vec = data[i]
        true_label = labels[i]
        
        best_dist = float('inf')
        predicted_label = "None (No Match)"
        
        for j in range(num_samples):
            if i == j: continue # Don't compare against self
            
            dist = calculate_cosine_distance(query_vec, data[j])
            if dist < best_dist:
                best_dist = dist
                predicted_label = labels[j]
        
        # Apply Threshold
        if best_dist > THRESHOLD:
            predicted_label = "None (No Match)"
            
        y_true.append(true_label)
        y_pred.append(predicted_label)

    # 3. Generate Report
    acc = accuracy_score(y_true, y_pred)
    
    print("\n" + "="*40)
    print(f"REAL SYSTEM ACCURACY: {acc * 100:.2f}%")
    print("="*40)
    
    print("\nDetailed Classification Report:")
    report = classification_report(y_true, y_pred, zero_division=0)
    print(report)
    
    # 4. Identifying Confusion Pairs
    print("\nPotential Confusion Analysis:")
    confused_count = 0
    for i in range(len(y_true)):
        if y_true[i] != y_pred[i]:
            print(f"  [!] '{y_true[i]}' was mistaken for '{y_pred[i]}'")
            confused_count += 1
            
    if confused_count == 0:
        print("  Excellent! No signs were confused in the template set.")

    # 5. Save results to file
    with open("REAL_METRICS_REPORT.txt", "w") as f:
        f.write("ISL-SIMILARITY STUDIO: SYSTEM METRICS\n")
        f.write("=====================================\n")
        f.write(f"Accuracy: {acc * 100:.2f}%\n")
        f.write(f"Threshold used: {THRESHOLD}\n\n")
        f.write("Full Report:\n")
        f.write(report)

    print("\nFull metrics saved to: REAL_METRICS_REPORT.txt")

if __name__ == "__main__":
    run_validation()
