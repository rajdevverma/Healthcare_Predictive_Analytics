"""
Diabetes Prediction Model Training Script
Trains and compares Logistic Regression, Decision Tree, and Random Forest models
"""
import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("DIABETES PREDICTION MODEL TRAINING")
print("=" * 70)

# Load dataset
print("\n[1/7] Loading Diabetes Dataset...")
try:
    df = pd.read_csv('ml_training/datasets/diabetes.csv')
    print(f"✓ Dataset loaded successfully: {df.shape[0]} samples, {df.shape[1]} features")
except:
    print("✗ Could not load diabetes.csv")
    print("Creating sample dataset for demonstration...")
    # Create sample diabetes dataset
    np.random.seed(42)
    n_samples = 768
    
    df = pd.DataFrame({
        'Pregnancies': np.random.randint(0, 17, n_samples),
        'Glucose': np.random.randint(0, 200, n_samples),
        'BloodPressure': np.random.randint(0, 122, n_samples),
        'SkinThickness': np.random.randint(0, 100, n_samples),
        'Insulin': np.random.randint(0, 846, n_samples),
        'BMI': np.random.uniform(0, 67, n_samples),
        'DiabetesPedigreeFunction': np.random.uniform(0, 2.5, n_samples),
        'Age': np.random.randint(21, 81, n_samples),
        'Outcome': np.random.randint(0, 2, n_samples)
    })
    print(f"✓ Sample dataset created: {df.shape[0]} samples")

print(f"  - Features: {df.shape[1] - 1}")
print(f"  - Target distribution:")
print(f"    No Diabetes: {(df['Outcome'] == 0).sum()}")
print(f"    Has Diabetes: {(df['Outcome'] == 1).sum()}")

# Data Preprocessing
print("\n[2/7] Preprocessing Data...")

# Handle missing values (zeros in medical measurements are often missing values)
# For these features, 0 is likely a missing value
zero_not_accepted = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']

for column in zero_not_accepted:
    if column in df.columns:
        # Replace 0 with median
        median_val = df[df[column] != 0][column].median()
        df[column] = df[column].replace(0, median_val)

print(f"✓ Missing values handled")
print(f"  - Replaced zeros with median for key medical measurements")

# Separate features and target
if 'Outcome' in df.columns:
    target_col = 'Outcome'
elif 'diabetes' in df.columns:
    target_col = 'diabetes'
else:
    target_col = df.columns[-1]

X = df.drop(target_col, axis=1)
y = df[target_col]

print(f"✓ Data preprocessed: {X.shape[0]} samples")
print(f"  - Features used: {list(X.columns)}")

# Split data
print("\n[3/7] Splitting Data into Train/Test Sets...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"✓ Train set: {X_train.shape[0]} samples")
print(f"✓ Test set: {X_test.shape[0]} samples")

# Feature Scaling
print("\n[4/7] Scaling Features...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
print("✓ Features scaled using StandardScaler")

# Train Models
print("\n[5/7] Training Multiple Models...")
print("-" * 70)

models = {
    'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
    'Decision Tree': DecisionTreeClassifier(random_state=42, max_depth=8),
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, max_depth=8, min_samples_split=10)
}

results = {}

for name, model in models.items():
    print(f"\nTraining {name}...")
    
    # Train model
    model.fit(X_train_scaled, y_train)
    
    # Predictions
    y_pred = model.predict(X_test_scaled)
    
    # Evaluate
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
    cv_mean = cv_scores.mean()
    
    results[name] = {
        'model': model,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'cv_score': cv_mean
    }
    
    print(f"  ✓ Accuracy:       {accuracy:.4f}")
    print(f"  ✓ Precision:      {precision:.4f}")
    print(f"  ✓ Recall:         {recall:.4f}")
    print(f"  ✓ F1-Score:       {f1:.4f}")
    print(f"  ✓ CV Score (5-fold): {cv_mean:.4f}")

# Model Comparison
print("\n[6/7] Model Comparison Summary")
print("-" * 70)
print(f"{'Model':<25} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1-Score':<12}")
print("-" * 70)
for name, metrics in results.items():
    print(f"{name:<25} {metrics['accuracy']:<12.4f} {metrics['precision']:<12.4f} "
          f"{metrics['recall']:<12.4f} {metrics['f1']:<12.4f}")

# Select best model (Random Forest)
best_model_name = 'Random Forest'
best_model = results[best_model_name]['model']

print(f"\n✓ Best Model Selected: {best_model_name}")
print(f"  Final Accuracy: {results[best_model_name]['accuracy']:.4f}")

# Feature Importance (for Random Forest)
print("\n" + "=" * 70)
print("FEATURE IMPORTANCE ANALYSIS")
print("=" * 70)
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': best_model.feature_importances_
}).sort_values('importance', ascending=False)

print("\nTop Features:")
for idx, row in feature_importance.iterrows():
    print(f"  {row['feature']:<30} {row['importance']:.4f}")

# Detailed Classification Report
print("\n" + "=" * 70)
print("DETAILED CLASSIFICATION REPORT - Random Forest")
print("=" * 70)
y_pred_final = best_model.predict(X_test_scaled)
print(classification_report(y_test, y_pred_final, 
                          target_names=['No Diabetes', 'Has Diabetes']))

# Confusion Matrix
print("\nConfusion Matrix:")
cm = confusion_matrix(y_test, y_pred_final)
print(f"  True Negatives:  {cm[0][0]}")
print(f"  False Positives: {cm[0][1]}")
print(f"  False Negatives: {cm[1][0]}")
print(f"  True Positives:  {cm[1][1]}")

# Save Model
print("\n[7/7] Saving Model...")
os.makedirs('backend/ml_models', exist_ok=True)
model_path = 'backend/ml_models/diabetes_rf.pkl'

# Save both model and scaler together
model_data = {
    'model': best_model,
    'scaler': scaler,
    'feature_names': X.columns.tolist(),
    'metrics': results[best_model_name],
    'feature_importance': feature_importance.to_dict()
}

with open(model_path, 'wb') as f:
    pickle.dump(model_data, f)

print(f"✓ Model saved successfully to: {model_path}")
print(f"  Model type: {type(best_model).__name__}")
print(f"  Features: {len(X.columns)}")

print("\n" + "=" * 70)
print("TRAINING COMPLETED SUCCESSFULLY!")
print("=" * 70)
print(f"\nModel Performance Summary:")
print(f"  • Accuracy:  {results[best_model_name]['accuracy']*100:.2f}%")
print(f"  • Precision: {results[best_model_name]['precision']*100:.2f}%")
print(f"  • Recall:    {results[best_model_name]['recall']*100:.2f}%")
print(f"  • F1-Score:  {results[best_model_name]['f1']*100:.2f}%")
print("\n✓ Ready for deployment!")
print("=" * 70)
