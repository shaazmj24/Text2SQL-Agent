from backend.llm_pipeline.client import ask_gemini

print(ask_gemini(""" 
                 Generate PostgreSQL SQL.

Schema:
users(user_id, created_at)

Question:
How many users exist?

Rules:
- Return ONLY the SQL query.
- Do not use markdown.
- Do not wrap in ```sql.
- Do not explain anything.
"""))    






