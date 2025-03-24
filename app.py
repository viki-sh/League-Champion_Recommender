from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import ast
from flask_cors import CORS

from sklearn.preprocessing import OneHotEncoder, MultiLabelBinarizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.compose import make_column_transformer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)

# Home page
@app.route('/')
def home():
    return render_template('index.html')

# Route to serve recommend.html (so JS works!)
@app.route('/recommend.html')
def recommend_html():
    return render_template('recommend.html')

# Load and process data
df = pd.read_csv("champs-stats.csv")

dfml = df.copy()
multi_label_cols = ['Class(es)', 'Legacy', 'Lane']
encoded_frames = []

for col in multi_label_cols:
    df[col] = df[col].apply(ast.literal_eval)
    mlb = MultiLabelBinarizer()
    encoded = pd.DataFrame(
        mlb.fit_transform(df[col]),
        columns=[f"{col}_{cls}" for cls in mlb.classes_],
        index=df.index
    )
    encoded_frames.append(encoded)

dfml = df.drop(columns=multi_label_cols).join(encoded_frames)
dfml['Abilities'] = dfml['Abilities'].fillna('')

preproc = make_column_transformer(
    (OneHotEncoder(), ['Resource', 'Adaptive']),
    (TfidfVectorizer(), 'Abilities'),
    remainder='passthrough'
)

champ_names = dfml['Name']
X = preproc.fit_transform(dfml.drop(columns=['Name']))
similarity_matrix = cosine_similarity(X)

def recommend_champions(champ_name, top_n=10):
    champ_name = champ_name.lower()
    lower_names = champ_names.str.lower()

    if champ_name not in lower_names.values:
        raise Exception("Champion not found")

    idx = lower_names[lower_names == champ_name].index[0]
    sim_scores = list(enumerate(similarity_matrix[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    top_matches = sim_scores[1:top_n + 1]
    return [(champ_names[i], score) for i, score in top_matches]

@app.route('/recommend')
def recommend():
    champ = request.args.get('champion')
    top_n = int(request.args.get('top_n', 10))

    try:
        results = recommend_champions(champ, top_n=top_n)
        return jsonify([
            {"champion": name, "similarity": round(sim, 2)}
            for name, sim in results
        ])
    except:
        return jsonify({"error": "Champion not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
