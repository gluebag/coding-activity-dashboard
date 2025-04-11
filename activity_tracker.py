#!/usr/bin/env python3
"""
GitHub Activity Tracker - Privacy-Preserving Edition
---------------------------------------------------
Generates insights about your GitHub coding activity without exposing sensitive information.
"""
import os
import datetime
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from github import Github
from collections import Counter
import re

# Create output directories
os.makedirs("dashboard", exist_ok=True)
os.makedirs("reports", exist_ok=True)

# GitHub authentication
github_token = os.getenv("GITHUB_TOKEN")
if not github_token:
    raise ValueError("No GitHub token found. Please set the GITHUB_TOKEN environment variable.")

g = Github(github_token)
user = g.get_user()
username = user.login

# Time periods
now = datetime.datetime.now()
last_week = now - datetime.timedelta(days=7)
last_month = now - datetime.timedelta(days=30)
last_year = now - datetime.timedelta(days=365)

print(f"Analyzing GitHub activity for {username}...")

def sanitize_commit_message(message):
    """Remove sensitive information from commit messages."""
    # Extract emoji/prefix if present
    emoji_match = re.match(r'^([\W]+|\w+\([\w-]+\):)\s*(.*)', message)
    prefix = ""
    content = message
    
    if emoji_match:
        prefix = emoji_match.group(1)
        content = emoji_match.group(2)
    
    # Truncate long messages
    if len(content) > 80:
        content = content[:77] + "..."
    
    # Replace specific project names with generic terms
    sensitive_terms = {
        # Add your sensitive terms here
        "client-name": "client-project",
        "internal-project": "enterprise-system",
        "secret-feature": "new-feature"
    }
    
    for term, replacement in sensitive_terms.items():
        content = re.sub(re.escape(term), replacement, content, flags=re.IGNORECASE)
    
    return f"{prefix} {content}" if prefix else content

def get_repo_activity():
    """Gather activity data from all accessible repositories."""
    repo_data = []
    commit_data = []
    language_counter = Counter()
    commit_type_counter = Counter()
    
    # Process repositories
    for repo in user.get_repos():
        # Skip archived repos
        if repo.archived:
            continue
            
        try:
            # Get repository data
            repo_info = {
                "name": repo.name,
                "private": repo.private,
                "updated_at": repo.updated_at,
                "size": repo.size,
                "stars": repo.stargazers_count,
                "language": repo.language or "Unknown"
            }
            
            # Get language data
            languages = repo.get_languages()
            for lang, bytes_count in languages.items():
                language_counter[lang] += bytes_count
            
            # Get recent commits
            recent_commits = []
            
            try:
                for commit in repo.get_commits(since=last_month):
                    if not commit.author or not commit.author.login == username:
                        continue
                        
                    # Determine commit type based on message
                    commit_message = commit.commit.message
                    
                    # Extract commit type
                    commit_type = "other"
                    if re.search(r'fix|bug|issue', commit_message, re.IGNORECASE):
                        commit_type = "fix"
                    elif re.search(r'feat|feature|add', commit_message, re.IGNORECASE):
                        commit_type = "feature"
                    elif re.search(r'refactor', commit_message, re.IGNORECASE):
                        commit_type = "refactor"
                    elif re.search(r'test', commit_message, re.IGNORECASE):
                        commit_type = "test"
                    elif re.search(r'docs|documentation', commit_message, re.IGNORECASE):
                        commit_type = "docs"
                    elif re.search(r'perf|performance', commit_message, re.IGNORECASE):
                        commit_type = "performance"
                        
                    commit_type_counter[commit_type] += 1
                    
                    # Process commit
                    clean_message = sanitize_commit_message(commit_message)
                    commit_info = {
                        "repo": repo.name,
                        "repo_private": repo.private,
                        "date": commit.commit.author.date.isoformat(),
                        "message": clean_message,
                        "type": commit_type
                    }
                    commit_data.append(commit_info)
                    recent_commits.append(commit_info)
                    
            except Exception as e:
                print(f"Error getting commits for {repo.name}: {e}")
                
            # Add commit count
            repo_info["recent_commits"] = len(recent_commits)
            repo_data.append(repo_info)
                
        except Exception as e:
            print(f"Error processing repository {repo.name}: {e}")
    
    return repo_data, commit_data, language_counter, commit_type_counter

def generate_visualizations(commit_data, language_counter, commit_type_counter):
    """Generate visualizations for the dashboard."""
    # 1. Language distribution (pie chart)
    plt.figure(figsize=(10, 6))
    labels = [lang for lang, count in language_counter.most_common(8)]
    sizes = [count for lang, count in language_counter.most_common(8)]
    
    # Add "Other" category if needed
    if len(language_counter) > 8:
        other_count = sum(count for lang, count in language_counter.most_common()[8:])
        labels.append("Other")
        sizes.append(other_count)
    
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title('Language Distribution (by bytes of code)')
    plt.tight_layout()
    plt.savefig("dashboard/language_distribution.png")
    plt.close()
    
    # 2. Commit frequency by day (line chart)
    if commit_data:
        commit_df = pd.DataFrame(commit_data)
        commit_df['date'] = pd.to_datetime(commit_df['date'])
        commit_df['day'] = commit_df['date'].dt.date
        
        # Count commits by day
        daily_commits = commit_df.groupby('day').size()
        
        # Fill in missing days with zeros
        date_range = pd.date_range(end=now.date(), periods=30)
        daily_commits = daily_commits.reindex(date_range.date, fill_value=0)
        
        plt.figure(figsize=(12, 6))
        ax = sns.lineplot(x=daily_commits.index, y=daily_commits.values)
        ax.set_title("Daily Commit Activity (Last 30 Days)")
        ax.set_xlabel("Date")
        ax.set_ylabel("Number of Commits")
        plt.tight_layout()
        plt.savefig("dashboard/commit_frequency.png")
        plt.close()
    
    # 3. Commit types (bar chart)
    plt.figure(figsize=(10, 6))
    types = [t for t, c in commit_type_counter.most_common()]
    counts = [c for t, c in commit_type_counter.most_common()]
    
    sns.barplot(x=types, y=counts)
    plt.title("Commit Types (Last 30 Days)")
    plt.xlabel("Type")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig("dashboard/commit_types.png")
    plt.close()

def generate_dashboard(repo_data, commit_data, language_counter, commit_type_counter):
    """Generate HTML dashboard."""
    # Sort repositories by recent commit count
    active_repos = sorted([r for r in repo_data if r["recent_commits"] > 0], 
                       key=lambda x: x["recent_commits"], reverse=True)
    
    # Get recent commits, sorted by date
    if commit_data:
        commit_df = pd.DataFrame(commit_data)
        commit_df['date'] = pd.to_datetime(commit_df['date'])
        recent_commits = commit_df.sort_values('date', ascending=False).head(10)
    else:
        recent_commits = []
    
    # Calculate stats
    total_commits = len(commit_data)
    active_repo_count = len(active_repos)
    languages_used = len(language_counter)
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{username}'s Coding Activity Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{ padding-top: 2rem; padding-bottom: 2rem; }}
        .stat-card {{ height: 100%; }}
        .commit-message {{ font-family: monospace; }}
    </style>
</head>
<body>
    <div class="container">
        <header class="pb-3 mb-4 border-bottom">
            <h1 class="display-4">{username}'s Coding Activity</h1>
            <p class="lead">Last updated: {now.strftime('%Y-%m-%d %H:%M UTC')}</p>
        </header>
        
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="card stat-card">
                    <div class="card-body">
                        <h5 class="card-title">Recent Activity</h5>
                        <h2 class="display-4">{total_commits}</h2>
                        <p class="card-text">Commits in the last 30 days</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card stat-card">
                    <div class="card-body">
                        <h5 class="card-title">Active Projects</h5>
                        <h2 class="display-4">{active_repo_count}</h2>
                        <p class="card-text">Repositories with recent commits</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card stat-card">
                    <div class="card-body">
                        <h5 class="card-title">Technical Breadth</h5>
                        <h2 class="display-4">{languages_used}</h2>
                        <p class="card-text">Programming languages used</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>Language Distribution</h5>
                    </div>
                    <div class="card-body text-center">
                        <img src="language_distribution.png" alt="Language Distribution" class="img-fluid">
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>Commit Activity</h5>
                    </div>
                    <div class="card-body text-center">
                        <img src="commit_frequency.png" alt="Commit Frequency" class="img-fluid">
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>Commit Types</h5>
                    </div>
                    <div class="card-body text-center">
                        <img src="commit_types.png" alt="Commit Types" class="img-fluid">
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Most Active Repositories</h5>
                    </div>
                    <div class="card-body">
                        <ul class="list-group">
    """
    
    # Add active repositories
    for i, repo in enumerate(active_repos[:5]):
        privacy_badge = '<span class="badge bg-secondary">Private</span>' if repo["private"] else '<span class="badge bg-success">Public</span>'
        html += f"""
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                {repo["name"]} {privacy_badge}
                                <span class="badge bg-primary rounded-pill">{repo["recent_commits"]} commits</span>
                            </li>"""
    
    html += """
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5>Recent Commit Messages</h5>
                    </div>
                    <div class="card-body">
                        <ul class="list-group">
    """
    
    # Add recent commit messages
    for _, commit in recent_commits.iterrows():
        repo_name = commit["repo"]
        date = pd.to_datetime(commit["date"]).strftime("%Y-%m-%d")
        message = commit["message"]
        privacy_badge = '<span class="badge bg-secondary">Private</span>' if commit["repo_private"] else '<span class="badge bg-success">Public</span>'
        
        html += f"""
                            <li class="list-group-item">
                                <div class="d-flex w-100 justify-content-between">
                                    <h6 class="mb-1">{repo_name} {privacy_badge}</h6>
                                    <small>{date}</small>
                                </div>
                                <p class="mb-1 commit-message">{message}</p>
                            </li>"""
    
    html += """
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        
        <footer class="pt-5 my-5 text-muted border-top">
            Created with ❤️ by GitHub Actions &middot; &copy; 2025
        </footer>
    </div>
</body>
</html>
    """
    
    with open("dashboard/index.html", "w") as f:
        f.write(html)
    
    # Also save the data as JSON
    with open("reports/repo_activity.json", "w") as f:
        json.dump(repo_data, f, default=str)
        
    with open("reports/commit_activity.json", "w") as f:
        json.dump(commit_data, f, default=str)
        
    with open("reports/language_stats.json", "w") as f:
        json.dump({lang: count for lang, count in language_counter.items()}, f)

if __name__ == "__main__":
    print("Fetching repository and commit data...")
    repo_data, commit_data, language_counter, commit_type_counter = get_repo_activity()
    
    print(f"Processing {len(repo_data)} repositories and {len(commit_data)} commits...")
    
    print("Generating visualizations...")
    generate_visualizations(commit_data, language_counter, commit_type_counter)
    
    print("Creating dashboard...")
    generate_dashboard(repo_data, commit_data, language_counter, commit_type_counter)
    
    print("Activity tracker completed successfully!")
