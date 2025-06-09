import json
import sqlite3
import numpy as np
from sklearn.cluster import MiniBatchKMeans
import joblib
from openai import OpenAI
from database import DatabaseManager

DB_PATH = 'db.sqlite'
MODEL_PATH = 'kmeans_tags.pkl'
DRAFT_PATH = 'cluster_tags_draft.json'


def main():
    db = DatabaseManager(DB_PATH)
    rows = db.get_all_embeddings()
    if not rows:
        print('No embeddings found')
        return
    embeddings = np.array([json.loads(r[1]) for r in rows], dtype='float32')
    kmeans = MiniBatchKMeans(n_clusters=30, random_state=42, batch_size=500)
    kmeans.fit(embeddings)
    joblib.dump(kmeans, MODEL_PATH)
    print(f'Saved kmeans model to {MODEL_PATH}')

    # sample transcripts per cluster
    cluster_samples = {i: [] for i in range(30)}
    ids = [r[0] for r in rows]
    for vid, vec in zip(ids, embeddings):
        cid = int(kmeans.predict(vec.reshape(1, -1))[0])
        if len(cluster_samples[cid]) < 5:
            # fetch transcript
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute('SELECT content FROM transcript WHERE video_id = ?', (vid,))
            row = cur.fetchone()
            conn.close()
            if row:
                cluster_samples[cid].append(row[0][:500])
    client = OpenAI()
    draft = {}
    for cid, texts in cluster_samples.items():
        if not texts:
            continue
        joined = '\n'.join(texts)
        prompt = f"Suggest 5-10 concise tags that best represent these transcripts:\n{joined}"
        try:
            resp = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=100,
            )
            tag_line = resp.choices[0].message.content.strip()
            draft[str(cid)] = [t.strip().lower() for t in tag_line.split(',')]
        except Exception as e:
            print('Error generating tags for cluster', cid, e)
    with open(DRAFT_PATH, 'w') as f:
        json.dump(draft, f, indent=2)
    print(f'Wrote draft tag map to {DRAFT_PATH}')

if __name__ == '__main__':
    main()
