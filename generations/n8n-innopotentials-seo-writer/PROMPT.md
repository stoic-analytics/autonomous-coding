# n8n SEO Writer - Ralph Wiggum Loop Prompt

## Project Context

You are working on an n8n workflow automation that transforms URLs and PDFs into SEO-optimized WordPress blog posts for the DACH region.

**Project Directory:** /Users/stoic-analytics/git/autonomous-coding/generations/n8n-innopotentials-seo-writer

## Current State

Check the features database for current progress:
```bash
sqlite3 features.db "SELECT COUNT(*) as total, SUM(passes) as passing FROM features"
```

## Your Task

Iterate on this project to make features pass. Each iteration, you should:

1. **Check Status**: Query `features.db` to see which features are failing
2. **Identify Next Feature**: Pick the lowest priority failing feature to work on
3. **Implement/Fix**: Make changes to workflow, scripts, or configuration
4. **Verify**: If possible, test the change
5. **Update Feature**: If verified working, mark as passing in the database

## Key Files

- `workflow-exports/seo-writer-workflow.json` - Main n8n workflow
- `google-apps-script/approve-button.gs` - Google Sheets approval script
- `.env` - Configuration (Ollama model, ports, Sheet ID)
- `app_spec.txt` - Full project specification
- `features.db` - SQLite database tracking feature completion

## Features Database Schema

```sql
CREATE TABLE features (
  id INTEGER PRIMARY KEY,
  priority INTEGER,
  category TEXT,
  name TEXT,
  description TEXT,
  steps TEXT,  -- JSON array of verification steps
  passes INTEGER DEFAULT 0
);
```

## What You Can Work On Without External Services

1. **Workflow Structure**: Improve n8n workflow JSON (node connections, error handling)
2. **Ollama Prompts**: Refine prompts for keyword extraction, blog generation, image prompts
3. **Apps Script**: Enhance the Google Apps Script functionality
4. **Validation Logic**: Add input validation in workflow nodes
5. **Documentation**: Ensure docs match implementation
6. **Error Handling**: Add proper error branches in workflow

## What Requires External Services (Skip for Now)

- Google Sheets API integration testing
- WordPress publishing testing
- Actual Ollama API calls
- ComfyUI/Flux image generation
- SMTP email testing

## Completion Criteria

Output `LOOP_COMPLETE` when:
- All features that can be implemented without external services are done
- OR you've made maximum reasonable progress this iteration

## Iteration Instructions

1. Start by querying the features database
2. Pick ONE feature to work on
3. Make the necessary changes
4. Commit your changes with a descriptive message
5. Update the feature status if appropriate
6. Report what you did and what's next

## Output Format

At the end of each iteration, output:

```
ITERATION_SUMMARY:
- Feature worked on: [name]
- Changes made: [brief description]
- Files modified: [list]
- Feature status: [passing/still failing/blocked by external service]
- Next feature to tackle: [name or LOOP_COMPLETE if done]
```
