from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import ast
from flask_cors import CORS

from sklearn.preprocessing import OneHotEncoder, MultiLabelBinarizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.compose import make_column_transformer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
#makes flask object 

CORS(app)

#model 
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

#finding similarities
similarity_matrix = cosine_similarity(X)


def recommend_champions(champ_name, top_n=10):
    idx = champ_names[champ_names == champ_name].index[0]
    sim_scores = list(enumerate(similarity_matrix[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    top_matches = sim_scores[1:top_n + 1]  # skip itself
    return [(champ_names[i], score) for i, score in top_matches]

 

@app.route('/recommend')
#tells flask to watch for /recommend, which calls the function below

def recommend(): #called uppon /recommend. 
    champ = request.args.get('champion') #ex) /recommend?champion=Ahri, this gets "Ahri" and stores it in champ.
    top_n = int(request.args.get('top_n', 10)) #defaults to 10 

    try:
        results = recommend_champions(champ, top_n=top_n) #goes into recommender funcion, returns list of (name, similarity) pairs
        return jsonify([
            {"champion": name, "similarity": round(sim, 2)}
            for name, sim in results #makes a list of sictionaries for each result in json response 
        ])
    except:
        return jsonify({"error": "Champion not found"}), 404
    #the return is fetched by script.js


    
if __name__ == '__main__':
    app.run(debug=True)
