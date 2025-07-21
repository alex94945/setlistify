---
trigger: always_on
---

- run `conda activate setlistify` in all new terminal windows before running any other commands.
- do not run commands with `conda run` because it hides the output (eg use `uvicorn src.server:app --reload` NOT `conda run -n setlistify uvicorn src.server:app --reload`) 
- when using your read_file tool always specify start and end lines.