# dynamodb-table-copier

Copies a table's data from one DynamoDB instance to another

## Configuration
The application can be configured by modifying the `config.json` file located in the project root. Note that this supports separate configurations for different environments, with the `config.json`, `config.dev.json`, and `config.prod.json` files overwriting each other in that order. The default configuration has been left blank, as choosing defaults is difficult for custom applications.

| Key                       | Type                          | Description
| ------------------------- | ----------------------------- | -----------
| aws_credentials_file_path | String (Path)                 | (Optional) Provide a path to an AWS credentials file, if your IAM roles aren't set up properly.
| start_time_iso8601        | String (ISO 8601 Compliant)   | The start time (inclusive) that table items will be scanned from
| end_time_iso8601          | String (ISO 8601 Compliant)   | The end time (exclusive) that table items will be scanned to
| source_region_name        | String                        | The region string of your source DynamoDB instance
| source_table_name         | String                        | The table name of your source DynamoDB instance
| destination_endpoint_url  | String (Valid URL)            | The URL of the destination DynamoDB instance to copy items to
| destination_table_name    | String                        | The table name of your destination DynamoDB instance

## Getting up and running (local DynamoDB)
Currently, it's assumed that data will be copied from a AWS provisioned instance of DynamoDB to a locally hosted instance of DynamoDB. See [this link](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html) for information about getting a local DynamoDB instance up and running. This also assumes a relatively modern version of Python, so don't even think about trying 2.7. The instructions should play nice on Linux or in Powershell, but you should have an idea of what's going on.

1. Clone the repo: `https://github.com/naschorr/dynamodb-table-copier.git`

2. Create and activate the virtual environment:
```
python -m venv dynamodb-table-copier/
cd dynamodb-table-copier/
source bin/activate (on Linux) OR .\Scripts\activate (on Windows)
```

3. Install requirements: `pip install -r requirements.txt`

4. Start up the local DynamoDB instance with:
```
java -jar /path/to/DynamoDBLocal.jar -dbPath /path/to/local/database/storage/directory
```
Make sure to update the `jar` and `dbPath` options with the correct paths. Double check that the output looks something like the example below. It's crucial that the `DbPath` key exists, and that you know what port it's using.
```
Initializing DynamoDB Local with the following configuration:
Port:   8000
InMemory:       false
DbPath: /path/to/local/database/storage/directory
SharedDb:       false
shouldDelayTransientStatuses:   false
CorsParams:     *
```

5. Configure the dynamodb-table-copier's `config.json` file using the table above. Note that your `destination_endpoint_url` will likely be `http://localhost:8000` by default

6. Run the copier! Choose one of the following:
    - Run the `DynamoDBTableCopier` task in the VSCode Run and Debug menu
    - `cd code; python dynamo_table_copier.py` from the command line inside your activated virtual environment
