import os
import dateutil
import datetime
import boto3
from boto3.dynamodb.conditions import Attr
from typing import List, Dict, Any
from tqdm import tqdm

import utilities

## Config
CONFIG_OPTIONS = utilities.load_config()


class DynamoTableCopier:
    def __init__(self):
        ## Load the configuration
        self.credentials_path: str = CONFIG_OPTIONS.get("aws_credentials_file_path")
        self.source_table_name: str = CONFIG_OPTIONS.get("source_table_name")
        self.destination_table_name: str = CONFIG_OPTIONS.get("destination_table_name")
        self.start_time: datetime.datetime = dateutil.parser.parse(CONFIG_OPTIONS.get("start_time_iso8601"))
        self.end_time: datetime.datetime = dateutil.parser.parse(CONFIG_OPTIONS.get("end_time_iso8601"))

        self.source_resource = boto3.resource("dynamodb", region_name=CONFIG_OPTIONS.get("source_region_name"))
        self.destination_resource = boto3.resource(
            "dynamodb",
            region_name=CONFIG_OPTIONS.get("source_region_name"),
            endpoint_url=CONFIG_OPTIONS.get("destination_endpoint_url")
        )

        assert(self.source_resource is not None)
        assert(self.destination_resource is not None)

        self.source_table = self.source_resource.Table(self.source_table_name)
        self.destination_table = self._get_destination_table()

        assert(self.source_table is not None)
        assert(self.destination_table is not None)

        self._copy_table()

    ## Properties

    @property
    def credentials_path(self):
        return self._credentials_path


    @credentials_path.setter
    def credentials_path(self, value):
        if (not value):
            self._credentials_path = None
            return

        self._credentials_path = value
        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = self.credentials_path

    ## Methods

    def _get_destination_table(self):
        try:
            return self.destination_resource.create_table(
                AttributeDefinitions=self.source_table.attribute_definitions,
                TableName=self.destination_table_name,
                KeySchema=self.source_table.key_schema,
                ProvisionedThroughput={
                    "ReadCapacityUnits": self.source_table.provisioned_throughput.get("ReadCapacityUnits", 5),
                    "WriteCapacityUnits": self.source_table.provisioned_throughput.get("WriteCapacityUnits", 5),
                }
            )
        except Exception:
            return self.destination_resource.Table(self.destination_table_name)


    def _batch_write_items(self, table, items: List[Dict[str, Any]]):
        """Generically batch write the given list of dictionaries to the given table."""

        with table.batch_writer() as batch:
            for item in tqdm(items, desc="Batch copying items "):
                batch.put_item(
                    Item = item
                )


    def _copy_table(self):
        print(f"Starting table copy from {self.source_table_name} to {self.destination_table_name}, items between {self.start_time.isoformat()} and {self.end_time.isoformat()}")

        counter = 0
        response = {}
        do_while = True ## Very lazy do-while loop emulation
        while response.get("LastEvaluatedKey") or do_while:
            filter_expression = Attr("timestamp").gte(int(self.start_time.timestamp() * 1000)) & Attr("timestamp").lt(int(self.end_time.timestamp() * 1000))
            if (do_while):
                response = self.source_table.scan(FilterExpression=filter_expression)
            else:
                response = self.source_table.scan(
                    FilterExpression=filter_expression,
                    ExclusiveStartKey=response.get("LastEvaluatedKey")
                )

            items = response.get("Items", [])

            if (items):
                self._batch_write_items(self.destination_table, items)

                counter += len(items)
                print(f" Batch completed. Copied {counter} ({len(items)} new) items from {self.source_table_name} to {self.destination_table_name}.")

            do_while = False

        print("Complete!")


if (__name__ == "__main__"):
    DynamoTableCopier()
