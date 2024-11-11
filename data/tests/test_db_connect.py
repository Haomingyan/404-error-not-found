import unittest
import mongomock
import pymongo as pm
from unittest.mock import patch
import data.db_connect as dbc

class TestMongoFunctions(unittest.TestCase):
    @patch('mongo_handler.pm.MongoClient')
    def setUp(self, mock_client):
        # Set up a mock for pymongo.MongoClient
        self.mock_client = mongomock.MongoClient()
        mock_client.return_value = self.mock_client
        dbc.connect_db()

        # Insert sample data to use for tests
        self.collection = self.mock_client['gamesDB']['test_collection']
        self.sample_data = {
            'title': 'Chess',
            'players': 2
        }
        self.collection.insert_one(self.sample_data)


if __name__ == '__main__':
    unittest.main()