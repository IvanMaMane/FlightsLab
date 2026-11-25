# AI Usage Disclosure

<!--
Fill in this file before you submit. Submissions without it are not graded.
If you used no AI tools, delete everything below and write only:
No AI tools were used.
-->

## Tools used

- Tool and version: Google Gemini (Gemini 3 Flash)

## Conversation links

- Link 1: https://share.gemini.google/4DJffExH60vC

## What I used them for

- Debugging failing public tests across row validation, cross-file duplicate detection, CLI output directories, and extended query sorting/limiting.

## Which parts of the code were AI-generated or substantially AI-assisted

| File | Function or part | How (generated / modified / explained) |
| --- | --- | --- |
| `csv_loader.py` | `parse_files` | Modified — moved `seen = set()` outside the file loop so duplicate checks apply across all files in a folder. |
| `flight_parser.py` | `parse_csvs`, `write_response` | Modified — added `os.makedirs(..., exist_ok=True)` to automatically create missing parent directories for `-o` and `-r`. |
| `query.py` | `run_query` | Modified — fixed `sort_by` to sort by native values instead of `str()`, and fixed `limit` handling so `limit: 0` returns `[]`. |
| `validator.py` | `validate_row` | Modified — replaced `.isalnum()` with strict ASCII regex `r"[A-Za-z0-9]{2,8}"` for `flight_id`. |

## Key prompts

1. "The following is the labwork, the zip file that it came with + the 4 .py files that I modified in order to complete the labwork. Please check what errors I've made, due to the fact that some tests had failed."
2. "can you add these modifications to the following files?"

## What I changed or verified myself

- Implemented the initial solutions across `csv_loader.py`, `flight_parser.py`, `query.py`, and `validator.py` before debugging.
- Reviewed all suggested fixes, integrated them into the project workspace, and ran `python tests/run_public_tests.py` to verify all test groups passed.