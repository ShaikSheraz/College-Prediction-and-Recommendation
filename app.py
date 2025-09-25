from flask import Flask, render_template, request
import pandas as pd
import joblib
import numpy as np

app = Flask(__name__)

# --- Load models and encoders ---
best_model = joblib.load('outputs/best_admission_model.joblib')
le_exam = joblib.load('outputs/le_exam.joblib')
le_cat = joblib.load('outputs/le_cat.joblib')
le_branch = joblib.load('outputs/le_branch.joblib')
le_college = joblib.load('outputs/le_college.joblib')

# Load cutoffs
cutoffs_df = pd.read_csv('outputs/cutoffs.csv')

# --- Prediction function ---
def predict_admission(rank, exam, category, branch, college):
    # Normalize inputs
    exam = exam.strip().upper()
    category = category.strip().upper()
    branch = branch.strip().upper()
    college = college.strip().upper()
    
    # Encode
    try: exam_enc = le_exam.transform([exam])[0]
    except: exam_enc = 0
    try: cat_enc = le_cat.transform([category])[0]
    except: cat_enc = 0
    try: branch_enc = le_branch.transform([branch])[0]
    except: branch_enc = 0
    try: college_enc = le_college.transform([college])[0]
    except: college_enc = 0

    # Get cutoff
    subset = cutoffs_df[
        (cutoffs_df.exam.str.upper() == exam) &
        (cutoffs_df.branch.str.upper() == branch) &
        (cutoffs_df.category.str.upper() == category) &
        (cutoffs_df.college.str.upper() == college)
    ]
    if len(subset) > 0:
        cutoff = subset['cutoff'].values[0]
        rank_ratio = rank / cutoff
    else:
        # Missing cutoff → very low probability
        return {'admit': 0, 'probability': 5}

    # Prepare sample
    sample = pd.DataFrame([[rank_ratio, exam_enc, cat_enc, branch_enc, college_enc]],
                          columns=['rank_ratio','exam_enc','cat_enc','branch_enc','college_enc'])
    
    # Predict probability
    prob = best_model.predict_proba(sample)[:,1][0]
    admit = 1 if prob >= 0.5 else 0

    return {'admit': admit, 'probability': round(prob*100,2)}

# --- Recommendation function ---
def recommend_colleges(rank, exam, category, branch, threshold=50):
    recommendations = []
    for col in cutoffs_df['college'].unique():
        pred = predict_admission(rank, exam, category, branch, col)
        if pred['probability'] >= threshold:
            recommendations.append({'college': col, 'prob': pred['probability']})
    # Sort by probability descending
    recommendations = sorted(recommendations, key=lambda x: x['prob'], reverse=True)
    return recommendations

# --- Routes ---
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/predict', methods=['GET','POST'])
def predict():
    result = None
    if request.method == 'POST':
        rank = int(request.form['rank'])
        exam = request.form['exam']
        category = request.form['category']
        branch = request.form['branch']
        college = request.form['college']
        result = predict_admission(rank, exam, category, branch, college)
    return render_template('predict.html', result=result)

@app.route('/recommendation', methods=['GET','POST'])
def recommendation():
    recommendations = None
    if request.method == 'POST':
        rank = int(request.form['rank'])
        exam = request.form['exam']
        category = request.form['category']
        branch = request.form['branch']
        recommendations = recommend_colleges(rank, exam, category, branch)
    return render_template('recommendation.html', recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)
