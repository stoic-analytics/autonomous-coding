#!/usr/bin/env python3
"""
Feature Progress Dashboard
Serves a web UI at http://127.0.0.1:8888 showing feature completion status.

Usage:
    python dashboard.py <project_dir>
    python dashboard.py generations/n8n-linkedin-poster

The project_dir should contain a features.db SQLite database.
"""

import json
import sqlite3
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_PORT = 8888


def get_db_path(project_dir: str) -> Path:
    """Resolve the features.db path from a project directory."""
    path = Path(project_dir).resolve()
    return path / "features.db"


def get_features(db_path: Path) -> list[dict]:
    """Read all features from the database."""
    if not db_path.exists():
        return []
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.execute(
        "SELECT id, priority, category, name, description, steps, passes "
        "FROM features ORDER BY priority ASC, id ASC"
    )
    features = [dict(row) for row in cursor.fetchall()]
    conn.close()
    for f in features:
        if isinstance(f["steps"], str):
            try:
                f["steps"] = json.loads(f["steps"])
            except (json.JSONDecodeError, TypeError):
                f["steps"] = []
    return features


def get_stats(features: list[dict]) -> dict:
    """Calculate stats from features list."""
    total = len(features)
    passing = sum(1 for f in features if f["passes"])
    percentage = round((passing / total * 100), 1) if total > 0 else 0
    categories = {}
    for f in features:
        cat = f["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "passing": 0}
        categories[cat]["total"] += 1
        if f["passes"]:
            categories[cat]["passing"] += 1
    return {
        "total": total,
        "passing": passing,
        "pending": total - passing,
        "percentage": percentage,
        "categories": categories,
    }


def render_html(features: list[dict], stats: dict, project_name: str) -> str:
    """Render the dashboard HTML."""
    progress_color = "#10b981" if stats["percentage"] >= 80 else "#f59e0b" if stats["percentage"] >= 40 else "#6366f1"

    category_cards = ""
    for cat, cat_stats in sorted(stats["categories"].items()):
        cat_pct = round(cat_stats["passing"] / cat_stats["total"] * 100, 1) if cat_stats["total"] > 0 else 0
        cat_color = "#10b981" if cat_pct >= 80 else "#f59e0b" if cat_pct >= 40 else "#6366f1"
        category_cards += f"""
        <div class="category-card">
            <div class="category-header">
                <span class="category-name">{cat}</span>
                <span class="category-pct" style="color: {cat_color}">{cat_pct}%</span>
            </div>
            <div class="progress-bar-small">
                <div class="progress-fill-small" style="width: {cat_pct}%; background: {cat_color}"></div>
            </div>
            <div class="category-counts">{cat_stats['passing']}/{cat_stats['total']} features</div>
        </div>"""

    feature_rows = ""
    for f in features:
        status_class = "status-pass" if f["passes"] else "status-pending"
        status_text = "PASS" if f["passes"] else "PENDING"
        steps_count = len(f["steps"]) if isinstance(f["steps"], list) else 0
        feature_rows += f"""
        <tr class="feature-row">
            <td class="col-id">{f['id']}</td>
            <td class="col-priority">{f['priority']}</td>
            <td class="col-category"><span class="badge">{f['category']}</span></td>
            <td class="col-name">{f['name']}</td>
            <td class="col-steps">{steps_count}</td>
            <td class="col-status"><span class="{status_class}">{status_text}</span></td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name} - Feature Dashboard</title>
    <meta http-equiv="refresh" content="10">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: #0f1117;
            color: #e2e8f0;
            min-height: 100vh;
            padding: 2rem;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #2d3748;
        }}
        .header h1 {{ font-size: 1.5rem; font-weight: 600; }}
        .header .refresh-note {{ color: #64748b; font-size: 0.8rem; }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .stat-card {{
            background: #1a1f2e;
            border: 1px solid #2d3748;
            border-radius: 8px;
            padding: 1.25rem;
        }}
        .stat-label {{ color: #94a3b8; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; }}
        .stat-value {{ font-size: 2rem; font-weight: 700; margin-top: 0.25rem; }}

        .progress-section {{ margin-bottom: 2rem; }}
        .progress-bar {{
            height: 12px;
            background: #2d3748;
            border-radius: 6px;
            overflow: hidden;
            margin-top: 0.5rem;
        }}
        .progress-fill {{
            height: 100%;
            border-radius: 6px;
            transition: width 0.5s ease;
        }}
        .progress-label {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.25rem;
        }}
        .progress-label span {{ color: #94a3b8; font-size: 0.85rem; }}

        .categories-section {{ margin-bottom: 2rem; }}
        .categories-section h2 {{ font-size: 1.1rem; margin-bottom: 1rem; color: #e2e8f0; }}
        .categories-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 0.75rem;
        }}
        .category-card {{
            background: #1a1f2e;
            border: 1px solid #2d3748;
            border-radius: 6px;
            padding: 1rem;
        }}
        .category-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }}
        .category-name {{ font-size: 0.85rem; font-weight: 500; }}
        .category-pct {{ font-size: 0.85rem; font-weight: 600; }}
        .progress-bar-small {{
            height: 4px;
            background: #2d3748;
            border-radius: 2px;
            overflow: hidden;
            margin-bottom: 0.4rem;
        }}
        .progress-fill-small {{
            height: 100%;
            border-radius: 2px;
            transition: width 0.5s ease;
        }}
        .category-counts {{ color: #64748b; font-size: 0.75rem; }}

        .features-section {{ margin-bottom: 2rem; }}
        .features-section h2 {{ font-size: 1.1rem; margin-bottom: 1rem; color: #e2e8f0; }}
        .table-wrapper {{
            overflow-x: auto;
            border: 1px solid #2d3748;
            border-radius: 8px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }}
        thead {{
            background: #1a1f2e;
            position: sticky;
            top: 0;
        }}
        th {{
            text-align: left;
            padding: 0.75rem 1rem;
            color: #94a3b8;
            font-weight: 500;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-bottom: 1px solid #2d3748;
        }}
        td {{
            padding: 0.6rem 1rem;
            border-bottom: 1px solid #1e2433;
        }}
        .feature-row:hover {{ background: #1a1f2e; }}
        .col-id {{ width: 50px; color: #64748b; }}
        .col-priority {{ width: 60px; color: #64748b; }}
        .col-steps {{ width: 60px; color: #64748b; text-align: center; }}
        .col-status {{ width: 80px; }}
        .badge {{
            display: inline-block;
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 500;
            background: #2d3748;
            color: #94a3b8;
        }}
        .status-pass {{
            display: inline-block;
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 600;
            background: rgba(16, 185, 129, 0.15);
            color: #10b981;
        }}
        .status-pending {{
            display: inline-block;
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 600;
            background: rgba(99, 102, 241, 0.15);
            color: #818cf8;
        }}
        .empty-state {{
            text-align: center;
            padding: 3rem;
            color: #64748b;
        }}
        .empty-state p {{ margin-top: 0.5rem; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{project_name}</h1>
            <span class="refresh-note">Auto-refreshes every 10s</span>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Features</div>
                <div class="stat-value">{stats['total']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Passing</div>
                <div class="stat-value" style="color: #10b981">{stats['passing']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Pending</div>
                <div class="stat-value" style="color: #818cf8">{stats['pending']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Progress</div>
                <div class="stat-value" style="color: {progress_color}">{stats['percentage']}%</div>
            </div>
        </div>

        <div class="progress-section">
            <div class="progress-label">
                <span>Overall Progress</span>
                <span>{stats['passing']}/{stats['total']}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {stats['percentage']}%; background: {progress_color}"></div>
            </div>
        </div>

        <div class="categories-section">
            <h2>Categories</h2>
            <div class="categories-grid">
                {category_cards if category_cards else '<div class="empty-state"><p>No features yet</p></div>'}
            </div>
        </div>

        <div class="features-section">
            <h2>All Features</h2>
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Priority</th>
                            <th>Category</th>
                            <th>Name</th>
                            <th>Steps</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {feature_rows if feature_rows else '<tr><td colspan="6" class="empty-state">No features created yet. Run the initializer agent first.</td></tr>'}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>"""


class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the dashboard."""

    project_dir = ""
    project_name = ""

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/stats":
            self.send_json_response()
        else:
            self.send_html_response()

    def send_html_response(self):
        db_path = get_db_path(self.project_dir)
        features = get_features(db_path)
        stats = get_stats(features)
        html = render_html(features, stats, self.project_name)

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def send_json_response(self):
        db_path = get_db_path(self.project_dir)
        features = get_features(db_path)
        stats = get_stats(features)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(stats).encode("utf-8"))

    def log_message(self, format, *args):
        """Suppress default access logs for cleaner output."""
        pass


def main():
    if len(sys.argv) < 2:
        print("Usage: python dashboard.py <project_dir>")
        print("Example: python dashboard.py generations/n8n-linkedin-poster")
        sys.exit(1)

    project_dir = sys.argv[1]
    project_path = Path(project_dir).resolve()

    if not project_path.exists():
        print(f"Error: Directory not found: {project_path}")
        sys.exit(1)

    project_name = project_path.name
    db_path = get_db_path(str(project_path))

    if not db_path.exists():
        print(f"Warning: No features.db found at {db_path}")
        print("The dashboard will show empty state until features are created.")

    DashboardHandler.project_dir = str(project_path)
    DashboardHandler.project_name = project_name

    port = int(os.environ.get("DASHBOARD_PORT", DEFAULT_PORT))
    server = HTTPServer(("127.0.0.1", port), DashboardHandler)

    print(f"Feature Dashboard: http://127.0.0.1:{port}")
    print(f"Project: {project_name}")
    print(f"Database: {db_path}")
    print("Press Ctrl+C to stop")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
        server.shutdown()


if __name__ == "__main__":
    main()
