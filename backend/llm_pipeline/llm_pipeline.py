from llm_pipeline.client import ask_gemini


def parse_question(user_question):
    # LLM turns question into JSON
    pass


def route_context(parsed_question):
    # choose revenue.yaml, churn.yaml, users.yaml, etc.
    pass


def generate_sql(user_question, selected_context):
    # LLM generates SQL
    pass


def validate_sql(sql):
    # block unsafe / invented SQL
    pass


def generate_answer(user_question, sql_result):
    # LLM converts result into readable answer
    pass


def run_llm_pipeline(user_question):
    parsed = parse_question(user_question)
    context = route_context(parsed)
    sql = generate_sql(user_question, context)
    validate_sql(sql)
    result = run_sql(sql)
    answer = generate_answer(user_question, result)

    return {
        "sql": sql,
        "result": result,
        "answer": answer
    } 






    
    
    