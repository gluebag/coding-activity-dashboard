# GitHub Coding Activity Dashboard

![Last Updated](https://img.shields.io/github/last-commit/gluebag/coding-activity-dashboard?label=Last%20Updated&style=flat-square)
![GitHub Actions](https://img.shields.io/github/workflow/status/gluebag/coding-activity-dashboard/GitHub%20Activity%20Tracker?label=Dashboard%20Generator&style=flat-square)

## Overview

This repository powers a privacy-preserving dashboard that visualizes my GitHub coding activity across both public and private repositories. It's designed to provide transparent insights into my development work without exposing sensitive code or confidential project details.

**[View the Live Dashboard](https://gluebag.github.io/coding-activity-dashboard/)**

## Features

- **Language Distribution Analysis**: Breakdown of programming languages I regularly work with
- **Commit Activity Visualization**: Patterns and frequency of my coding contributions
- **Project Diversity**: Overview of active repositories and projects
- **Commit Message Analysis**: Sanitized examples of recent work (with sensitive information removed)
- **Commit Type Breakdown**: Categories of work (features, fixes, refactoring, etc.)

## How It Works

This dashboard uses GitHub Actions to automatically analyze my coding activity across all repositories I have access to. The workflow:

1. Runs weekly (and can be triggered manually)
2. Processes commit data, repository information, and language statistics
3. Sanitizes all data to remove sensitive information
4. Generates visualizations and an HTML dashboard
5. Publishes the results to GitHub Pages

## Privacy Measures

- Repository names for private projects are included but no code is exposed
- Commit messages are sanitized to remove client names and sensitive details
- No internal URLs or specific project identifiers are included
- All data is aggregated to show trends rather than specific implementation details

## Technologies Used

- **Python**: Core analysis and data processing
- **Pandas & Matplotlib**: Data analysis and visualization
- **GitHub Actions**: Automated workflow and deployment
- **GitHub Pages**: Dashboard hosting
- **Bootstrap**: Dashboard UI framework

## For Recruiters

This dashboard offers visibility into my active development work while respecting confidentiality agreements with clients and employers. It demonstrates:

- Consistency of contributions
- Technical diversity
- Coding habits and practices
- Project management approach

For a more comprehensive understanding of my skills and experience, please also see my pinned repositories and [professional website](https://attentiv.dev).

---

*Last updated: 2025-04-11*
