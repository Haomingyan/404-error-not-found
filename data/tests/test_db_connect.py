import unittest
import mongomock
import pymongo
from unittest.mock import patch
import data.db_connect as dbc

class TestMongoFunctions(unittest.TestCase):
    @patch('pymongo.MongoClient')
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

    def test_insert_one(self):
        new_doc = {
            'title': 'Monopoly',
            'players': 4
        }
        result = dbc.insert_one('test_collection', new_doc)
        self.assertIsNotNone(result.inserted_id)

    def test_fetch_one(self):
        filt = {'title': 'Chess'}
        result = dbc.fetch_one('test_collection', filt)
        self.assertIsNotNone(result)
        self.assertEqual(result['title'], 'Chess')
        self.assertEqual(result['players'], 2)

    def test_fetch_one_not_found(self):
        # Try to fetch a document that doesn't exist
        filt = {'title': 'Checkers'}
        result = dbc.fetch_one('test_collection', filt)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()