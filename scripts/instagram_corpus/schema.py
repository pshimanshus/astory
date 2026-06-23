SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS ingest_runs (
    run_id TEXT PRIMARY KEY,
    source TEXT,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS raw_objects (
    raw_object_id TEXT PRIMARY KEY,
    provider TEXT NOT NULL,
    run_id TEXT NOT NULL,
    object_type TEXT NOT NULL,
    source_url TEXT NOT NULL,
    request_url TEXT,
    response_status INTEGER,
    local_path TEXT NOT NULL,
    metadata_path TEXT,
    sha256 TEXT NOT NULL,
    captured_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS accounts (
    account_id TEXT PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    full_name TEXT,
    profile_url TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS posts (
    post_id TEXT PRIMARY KEY,
    shortcode TEXT NOT NULL UNIQUE,
    permalink TEXT NOT NULL,
    account_id TEXT,
    media_type TEXT,
    product_type TEXT,
    posted_at TEXT,
    caption TEXT NOT NULL DEFAULT '',
    raw_object_id TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(account_id) REFERENCES accounts(account_id),
    FOREIGN KEY(raw_object_id) REFERENCES raw_objects(raw_object_id)
);

CREATE TABLE IF NOT EXISTS post_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    post_id TEXT NOT NULL,
    run_id TEXT NOT NULL,
    raw_object_id TEXT,
    captured_at TEXT NOT NULL,
    caption TEXT NOT NULL DEFAULT '',
    media_type TEXT,
    child_count INTEGER,
    like_count INTEGER,
    comment_count INTEGER,
    view_count INTEGER,
    play_count INTEGER,
    source_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
    FOREIGN KEY(raw_object_id) REFERENCES raw_objects(raw_object_id)
);

CREATE TABLE IF NOT EXISTS assets (
    asset_id TEXT PRIMARY KEY,
    post_id TEXT NOT NULL,
    asset_index INTEGER NOT NULL,
    media_type TEXT,
    source_url TEXT,
    display_url TEXT,
    media_file_id TEXT,
    status TEXT NOT NULL DEFAULT 'expected',
    metadata_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
    FOREIGN KEY(media_file_id) REFERENCES media_files(media_file_id),
    UNIQUE(post_id, asset_index)
);

CREATE TABLE IF NOT EXISTS media_files (
    media_file_id TEXT PRIMARY KEY,
    sha256 TEXT NOT NULL UNIQUE,
    local_path TEXT NOT NULL,
    source_url TEXT,
    mime_type TEXT,
    byte_count INTEGER,
    width INTEGER,
    height INTEGER,
    duration_seconds REAL,
    variant TEXT,
    raw_object_id TEXT,
    rights_scope TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(raw_object_id) REFERENCES raw_objects(raw_object_id)
);

CREATE TABLE IF NOT EXISTS metric_observations (
    observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value INTEGER,
    status TEXT NOT NULL DEFAULT 'available',
    source TEXT NOT NULL,
    run_id TEXT,
    raw_object_id TEXT,
    observed_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
    FOREIGN KEY(raw_object_id) REFERENCES raw_objects(raw_object_id)
);

CREATE TABLE IF NOT EXISTS comments (
    comment_id TEXT PRIMARY KEY,
    post_id TEXT NOT NULL,
    author_username TEXT,
    text TEXT NOT NULL,
    like_count INTEGER,
    posted_at TEXT,
    raw_object_id TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
    FOREIGN KEY(raw_object_id) REFERENCES raw_objects(raw_object_id)
);

CREATE TABLE IF NOT EXISTS annotations (
    annotation_id TEXT PRIMARY KEY,
    post_id TEXT,
    asset_id TEXT,
    annotation_type TEXT NOT NULL,
    label TEXT,
    notes TEXT NOT NULL DEFAULT '',
    source TEXT NOT NULL,
    created_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
    FOREIGN KEY(asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ocr_results (
    ocr_result_id TEXT PRIMARY KEY,
    asset_id TEXT NOT NULL,
    engine TEXT NOT NULL,
    status TEXT NOT NULL,
    full_text TEXT NOT NULL DEFAULT '',
    mean_confidence REAL,
    lines_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rag_chunks (
    chunk_id TEXT PRIMARY KEY,
    post_id TEXT,
    asset_id TEXT,
    chunk_type TEXT NOT NULL,
    source_url TEXT,
    text TEXT NOT NULL,
    rights_scope TEXT NOT NULL DEFAULT 'third_party_analysis_only',
    raw_object_ids TEXT NOT NULL DEFAULT '[]',
    gap_ids TEXT NOT NULL DEFAULT '[]',
    evidence_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
    FOREIGN KEY(asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS gaps (
    gap_id TEXT PRIMARY KEY,
    post_id TEXT,
    asset_id TEXT,
    gap_type TEXT NOT NULL,
    status TEXT NOT NULL,
    reason TEXT NOT NULL,
    source TEXT NOT NULL,
    created_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
    FOREIGN KEY(asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE,
    UNIQUE(post_id, asset_id, gap_type, source)
);

CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    job_type TEXT NOT NULL,
    status TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 0,
    target_id TEXT,
    run_id TEXT,
    payload_json TEXT NOT NULL DEFAULT '{}',
    attempts INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""
