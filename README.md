# CobraPinger

CobraPinger is a totally dank command line utility for monitoring youtubers you care about. It looks at an RSS for your favorite youtube channels every minute and when it sees a new video:

1) Downloads the transcript
2) Sends it to OpenAI for summarization and embedding.
3) Posts in a discord channel with a notification and the summary.
4) Feeds a website to visualize the information.

That's most definitely what's up!

# Running the web server

- Local Development: `python3 web.py`
- Run with Gunicorn web server: `./web_nonprod.sh`
- Production: `./web_prod.sh` (linux only)

## FAISS Embedding Index

On startup CobraPinger loads all video embeddings from SQLite into an in-memory
FAISS index. This powers retrieval augmented generation for the Council of
Advisors feature. New embeddings are appended to the index whenever a video is
processed. If the index ever gets out of sync you can rebuild it by restarting
the application or choosing the database rebuild option from the menu.

## Tagging System

Each transcript is assigned tags using a combination of retrieval augmented
generation and a global taxonomy. On ingest we look up tags from similar videos
and ask GPT for new suggestions. A MiniBatchKMeans model assigns every video to
a cluster which maps to a small set of base tags. All generated tags are snapped
to this approved vocabulary using embeddings.

To retrain the clustering model run `python retrain_taxonomy.py`. This will
produce `kmeans_tags.pkl` and a draft `cluster_tags_draft.json` for manual
editing. After curation save your mapping as `cluster_tag_map.json`.
It is recommended to rerun this script monthly or after processing roughly a
thousand new videos. Set up a cron job if desired.

### Migration Utilities

Two command-line helpers assist with moving existing data to the new tagging
system:

```
python cobrapinger.py --build-cluster-map   # train clusters and create draft tag map
python cobrapinger.py --retag-existing     # regenerate tags for all stored videos
```

# Credits

* Two idiots in a bear costume with a passion for food hacks.
* The AI
