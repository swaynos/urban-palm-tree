import asyncio
import json
import logging
import os
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from inference import parse_json_response


class TestParseJsonResponse(unittest.TestCase):

    def setUp(self):
        self.logger = Mock(spec=logging.Logger)

    def test_valid_json(self):
        json_str = json.dumps({
            "match-status": "IN-MATCH",
            "in-match-status": "LIVE-MATCH",
            "minimap": "YES"
        })
        result = asyncio.run(parse_json_response(self.logger, json_str))
        self.assertIsNotNone(result)
        self.assertEqual(result["match-status"], "IN-MATCH")
        self.assertEqual(result["in-match-status"], "LIVE-MATCH")
        self.assertEqual(result["minimap"], "YES")
        self.logger.error.assert_not_called()

    def test_invalid_match_status(self):
        json_str = json.dumps({
            "match-status": "INVALID",
            "in-match-status": "LIVE-MATCH",
            "minimap": "YES"
        })
        result = asyncio.run(parse_json_response(self.logger, json_str))
        self.assertIsNotNone(result)
        self.assertEqual(result["match-status"], "INVALID")
        self.logger.error.assert_any_call("Invalid value for 'match-status': INVALID. 'match-status' is expected to be one of: IN-MATCH, IN-MENU")

    def test_invalid_in_match_status(self):
        json_str = json.dumps({
            "match-status": "IN-MATCH",
            "in-match-status": "INVALID",
            "minimap": "YES"
        })
        result = asyncio.run(parse_json_response(self.logger, json_str))
        self.assertIsNotNone(result)
        self.assertEqual(result["in-match-status"], "INVALID")
        self.logger.error.assert_any_call("Invalid value for 'in-match-status': INVALID. 'in-match-status' must be one of: NONE, INSTANT-REPLAY, LIVE-MATCH")

    def test_invalid_minimap(self):
        json_str = json.dumps({
            "match-status": "IN-MATCH",
            "in-match-status": "LIVE-MATCH",
            "minimap": "INVALID"
        })
        result = asyncio.run(parse_json_response(self.logger, json_str))
        self.assertIsNotNone(result)
        self.assertEqual(result["minimap"], "INVALID")
        self.logger.error.assert_any_call("Invalid value for 'minimap': INVALID. 'minimap' must be one of: YES, NO")

    def test_json_decode_error(self):
        json_str = "invalid json"
        result = asyncio.run(parse_json_response(self.logger, json_str))
        self.assertIsNone(result)
        self.logger.error.assert_any_call("Error parsing the json string: invalid json")

    def test_general_exception(self):
        json_str = json.dumps({"match-status": "IN-MATCH"})
        mock_exception = Exception("Some error")
        with patch('json.loads', side_effect=mock_exception):
            result = asyncio.run(parse_json_response(self.logger, json_str))
            self.assertIsNone(result)
            self.logger.error.assert_any_call(f"Error processing the json string: {json_str}")
            self.logger.error.assert_any_call(mock_exception)

if __name__ == '__main__':
    unittest.main()
