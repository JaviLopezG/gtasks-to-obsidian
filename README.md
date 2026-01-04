# Google Tasks to Obsidian Converter

A simple Python script to convert Google Tasks data (exported via Google Takeout) into Obsidian-compatible Markdown files.

## Features

- **Hierarchy Preserved:** Reconstructs the parent/child structure of tasks using indentation.
    
- **Metadata:** Retains due dates, completion dates, and API IDs (hidden in HTML tags for cleaner UI).
    
- **Notes:** Imports task descriptions as blockquotes.
    
- **Obsidian Ready:** Formats tasks using standard Markdown checkboxes (`-[ ]` / `-[x]`).
    

## Usage

1. **Export Data:** Go to [Google Takeout](https://takeout.google.com/ "null") and export **Google Tasks**.
    
2. **Place File:** Extract the zip and place `Tasks.json` in the root directory of this repository.
    
3. **Run Script:**
    
    ```
    python gtasks_to_obsidian.py
    ```
    
4. **Output:** The script generates a folder named `Obsidian_Tasks` (configurable via `OUTPUT_DIR` in the script) containing one `.md` file per task list.
    

## Configuration

You can modify the constants at the top of `gtasks_to_obsidian.py` if you need to change the input filename or output directory name.

# Import

Copy the Google-Tasks folder to your vault or create a new one. This folder already contains md files with your tasks lists.

# Query

Install the community plugin Tasks and create a query to get your pending tasks:
``````
```tasks
not done
path includes Google-Tasks/Planning.md
hide backlink
hide edit button
hide task count
short mode
```
``````


