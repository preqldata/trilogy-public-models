from preql import Environment
from preql.constants import DEFAULT_NAMESPACE
from preql.core.models import (
    Concept,
    Datasource,
    Select,
    ProcessedShowStatement,
)
from preql.core.processing.concept_strategies_v2 import source_concepts
from preql.executor import Executor
from preql.parser import parse_text
from preql.core.internal import INTERNAL_NAMESPACE

def safe_address(input: Concept):
    if input.namespace == DEFAULT_NAMESPACE:
        return input.name
    return input.address


def validate_dataset(
    dataset: Datasource, environment: Environment, executor: Executor, dry_run_client
):
    # TODO: move ths into executor so we don't need this import
    from google.cloud.bigquery import QueryJobConfig

    validation_query = (
        "SELECT\n "
        + ",\n\t".join([safe_address(x) for x in dataset.concepts])
        + " LIMIT 0;"
    )

    try:
        _, parsed = parse_text(validation_query, environment)
        processed: list[Select] = [x for x in parsed if isinstance(x, Select)]
        sql = executor.generator.generate_queries(environment, processed)
    except Exception as e:
        print(validation_query)
        raise e
    for statement in sql:
        if isinstance(statement, ProcessedShowStatement):
            continue
        compiled_sql = ""
        # Start the query, passing in the extra configuration.
        try:
            # for UI execution, cap the limit
            compiled_sql = executor.generator.compile_statement(statement)

            # TODO: implement this
            # rs = executor.engine.dry_run(compiled_sql)
            job_config = QueryJobConfig(dry_run=True, use_query_cache=False)
            query_job = dry_run_client.query(
                compiled_sql, job_config=job_config
            )  # Make an API request.
        except Exception as e:
            print("Failed validation on:")
            print(validation_query)
            print(compiled_sql)
            raise e

        # TODO: do something interesting with cost modeling?
        #
        print(
            "This query will process {} bytes.".format(query_job.total_bytes_processed)
        )


def validate_datasource_grain(datasource):
    # TODO: check that count(*) at datasource grain = 1
    # CON: this requires running an real query
    pass


def validate_concept(concept: Concept, env):
    if concept.namespace == INTERNAL_NAMESPACE:
        return
    source_concepts([concept], [], environment=env)


def validate_model(model: Environment, executor: Executor, dry_run_client):
    for dataset in model.datasources.values():
        validate_dataset(dataset, model, executor, dry_run_client)
    for concept in model.concepts.values():
        validate_concept(concept, model)
