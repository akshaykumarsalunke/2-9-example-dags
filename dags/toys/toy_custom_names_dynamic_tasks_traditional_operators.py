"""
### Toy DAG to show how to use custom names for dynamic tasks - traditional operators

This DAG queries the fruityvice API for information about all fruits. 
It then creates a dynamically mapped task printing the sugar content of each fruit, 
with the dynamically mapped task instances being named after the fruit.
"""

from airflow.decorators import dag, task
from airflow.models.baseoperator import chain
from airflow.operators.bash import BashOperator
import requests


@dag(
    start_date=None,
    schedule=None,
    catchup=False,
    doc_md=__doc__,
    tags=["Dynamic Task Mapping", "2-9", "toy"],
)
def toy_custom_names_dynamic_tasks_traditional_operators():
    @task
    def get_fruits() -> list[dict]:

        r = requests.get(f"https://www.fruityvice.com/api/fruit/all").json()

        for fruit in r:
            fruit.update(fruit.pop("nutritions"))

        for fruit in r:
            for k, v in fruit.items():
                fruit[k] = str(v)

        return r

    get_fruits_obj = get_fruits()

    # NEW in Airflow 2.9: Define custom names for the map index
    map_fruits = BashOperator.partial(
        task_id="map_fruits",
        bash_command='echo "$name sugar content: $sugar"',
        map_index_template="This task is about {{ task.env['name'] }}",  # retrieving the fruit name from the input dictionary
    ).expand(env=get_fruits_obj)

    chain(get_fruits_obj, map_fruits)


toy_custom_names_dynamic_tasks_traditional_operators()
