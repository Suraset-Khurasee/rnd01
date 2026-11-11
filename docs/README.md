---
layout: default
title: Documents
---

# Documents

This folder is the project log. Add one Markdown file per topic, experiment, meeting, or decision.

## Add a document

1. Create a file in `docs/`, for example `docs/pick-and-place-test-01.md`.
2. Start it with front matter:

   ```yaml
   ---
   layout: default
   title: Pick and place test 01
   ---
   ```

3. Write the document using normal Markdown.
4. Add a link to this page or `index.md`.
5. Commit and push to `main`. GitHub Pages will deploy it automatically.

## Suggested log format

```markdown
# Experiment title

**Date:** 2026-11-11  
**Objective:** What are you testing?

## Setup

Describe the robot, controller, software, object, and destination.

## Results

Record what happened, measurements, issues, and screenshots or links.

## Next steps

Record the next change to try.
```

## Available documents

- [Project brief](project-brief.md)
- [Milestones](milestones.md)
- [Safety and experiment log](experiment-log.md)
