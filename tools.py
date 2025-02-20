from typing import Dict, Callable

import pandas as pd
import psycopg2
from ollama import Client

client = Client(
    host='http://10.10.8.15:11434',
)

messages = [{'role': 'user', 'content': f"get the data for date 202207"}]


# def generate_query(schema: str, table_name: str, condition: dict, operator: str):
#     prompt = f"""
#             act as database engineer, make query for table {schema}.{table_name} from condition
#             {condition} and operator is {operator}. Make sure to return the query only
#         """
#
#     response = client.chat(
#         model='llama3.2',
#         messages=[{'role': 'user', 'content': f"Model being used is 'llama3.2'.{prompt}"}],
#     )
#     return response

def get_data(date: str) -> str | None:
    host = "10.10.8.60"
    port = "5432"
    database = "denodo"
    user = "denodo_user"
    password = "denodo_pass_12#$"

    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )
    query = f"""
        select thbllap, jenislap, unitap, label, jmlkwh from pln.lp l
        where jenislap = 'NORMAL' and label != 'JUMLAH' and thbllap = '{date}'
    """
    df = pd.read_sql(query, conn)
    return df.to_markdown()


get_data_tool = {
    'type': 'function',
    'function': {
        'name': 'get_data',
        'description': 'Get the data from query return as dictionary',
        'parameters': {
            'type': 'object',
            'required': ['date'],
            'properties': {
                'date': {'type': 'string', 'description': 'The date of the data (e.g., 202401, 202402)'},
            },
        },
    },
}

available_functions: Dict[str, Callable] = {
    'get_data': get_data,
}

response = client.chat(
    model='llama3.2',
    messages=messages,
    tools=[get_data_tool],
)

if response.message.tool_calls:
    for tool in response.message.tool_calls:
        if function_to_call := available_functions.get(tool.function.name):
            print('Calling function:', tool.function.name)
            print('Arguments:', tool.function.arguments)
            print('Function output:', function_to_call(**tool.function.arguments))
            output = function_to_call(**tool.function.arguments)
            messages.append({
                'role': 'tool',
                'content': output
            })
        else:
            print('Function', tool.function.name, 'not found')

messages.append({'role': 'user', 'content': f"summarize the data like max min or average"})

response = client.chat(
    model='llama3.2',
    messages=messages,
)
print(response.message.content)

# response = generate_query('pln', 'lp', {"thbllap":"202207","jenislap":"LPB","unitap":"55SLT","label":"S"}, 'AND')
# get_data(response)
