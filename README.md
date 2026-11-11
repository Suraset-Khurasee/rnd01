# CE-0169 documentation

This is a simple Markdown-first GitHub Pages site for **CE-0169: Nero Robotic Arm Teleoperation**.

## Add documentation

Put Markdown files in `docs/`. Copy `docs/template.md`, give the page a title, and add front matter:

```yaml
---
layout: default
title: My document
---
```

Use `docs/README.md` for the full logging format and current document list.

## Local preview

The site is built by Jekyll in GitHub Actions. To preview locally, install Jekyll and run:

```sh
bundle exec jekyll serve
```

## Deployment

Push commits to `main`. The workflow builds the Markdown files and deploys them automatically to:

<https://suraset-khurasee.github.io/rnd01/>
