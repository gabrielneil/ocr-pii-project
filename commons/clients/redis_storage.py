import json

import redis


class RedisStorage:
    """
    A client to interact with Redis for storing, retrieving, and deleting data.

    The RedisStorage class provides methods for storing, retrieving, and deleting data in a Redis instance.
    The data is stored under composite keys based on the job ID and data type.

    """

    def __init__(self, host="localhost", port=6379, db=0):
        """
        Initializes the RedisStorage with a connection to the Redis database.

        Parameters
        ----------
        host : str, optional
            The hostname or IP address of the Redis server (default is "localhost").
        port : int, optional
            The port number on which the Redis server is listening (default is 6379).
        db : int, optional
            The Redis database number to use (default is 0).
        """
        self.client = redis.Redis(host=host, port=port, db=db)

    def store(self, key, data_type, data):
        """
        Store data in Redis under a composite key (key:data_type).

        The data is serialized as a JSON string and stored in Redis under a key formed by
        concatenating the `key` and `data_type`, separated by a colon.

        Parameters
        ----------
        key : str
            The base key (e.g., a job ID) to associate the data with.
        data_type : str
            A string representing the type of data (e.g., "bounding_boxes" or "pii_terms").
        data : any
            The data to be stored, which will be serialized into JSON format.

        """

        redis_key = f"{key}:{data_type}"
        self.client.set(redis_key, json.dumps(data))
        print(f"Stored {data_type} for job_id {key} in Redis")

    def retrieve(self, key, data_type):
        """
        Retrieve data from Redis based on a composite key (key:data_type).

        The data is retrieved from Redis using a composite key formed by concatenating
        the `key` and `data_type`. If data is found, it is deserialized from JSON format.

        Parameters
        ----------
        key : str
            The base key (e.g., a job ID) to retrieve the data for.
        data_type : str
            A string representing the type of data to retrieve (e.g., "bounding_boxes" or "pii_terms").

        Returns
        -------
        dict or None
            The data retrieved from Redis, deserialized from JSON format. If no data is found, `None` is returned.

        """
        redis_key = f"{key}:{data_type}"
        data_json = self.client.get(redis_key)
        if data_json:
            return json.loads(data_json)
        return None

    def delete(self, key):
        """
        Delete all related data (bounding boxes and PII terms) for a given img_id.

        This method deletes the keys associated with both the "bounding_boxes" and "pii_terms"
        for the given `key` (img ID) in Redis.

        Parameters
        ----------
        key : str
            The base key (e.g., an img ID) for which all related data should be deleted.

        """
        self.client.delete(f"{key}:bounding_boxes")
        self.client.delete(f"{key}:pii_terms")
        print(f"Deleted data for job_id {key} from Redis")
