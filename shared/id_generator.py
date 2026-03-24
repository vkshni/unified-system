# Shared ID Generator

from uuid import uuid4


# generate uuid
def generate_uuid() -> str:

    id = str(uuid4())
    return id


# generate incremental ids
def generate_incremental_id(system_name, counter_file):

    import json

    with open(counter_file, "r+") as f:

        data = json.load(f)

        if system_name not in data:
            raise ValueError("system name not found")

        counter = data[system_name]
        counter += 1

        data[system_name] = counter
        json.dump(data, f, indent=4)

    return counter


print(generate_incremental_id("tasks", "data\counter.json"))
