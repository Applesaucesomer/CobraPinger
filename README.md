# CobraPinger

CobraPinger is a totally dank command line utility for monitoring youtubers you care about. It looks at an RSS for your favorite youtube channels every minute and when it sees a new video:

1) Downloads the transcript
2) Sends it to OpenAI for summarization and embedding.
3) Posts in a discord channel with a notification and the summary.
4) Feeds a website to visualize the information.

## Dependencies

Install Python requirements from `requirements.txt`. This includes the
`openai-whisper` and `pytube` packages used for the transcript fallback.
In addition, `ffmpeg` must be installed for Whisper transcription
(e.g. `apt install ffmpeg`).

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

## Whisper Fallback

Use the `get_transcript(video_id, video_url)` helper to retrieve transcripts.
It first attempts the YouTube transcript API and falls back to OpenAI Whisper if
that fails. Control the Whisper model with the `WHISPER_MODEL` environment
variable (defaults to `base.en`).

If the fallback fails with an error, verify `ffmpeg` is installed and that the
YouTube URL is accessible. Errors like `HTTP Error 400` usually indicate the
video cannot be downloaded, often due to regional restrictions or an invalid
link.

# Credits

* Two idiots in a bear costume with a passion for food hacks.
* The AI
