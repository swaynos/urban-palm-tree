import asyncio
import json
import logging
import os
import sys
import unittest
from unittest.mock import Mock, patch, AsyncMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from inference import preprocess_json_string, parse_json_response

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
        self.assertIsNone(result["match-status"])
        #self.logger.warning.assert_any_call("Invalid match-status: INVALID, 'match-status' is expected to be one of: IN-MATCH, IN-MENU")
        
    def test_invalid_in_match_status(self):
        json_str = json.dumps({
            "match-status": "IN-MATCH",
            "in-match-status": "INVALID",
            "minimap": "YES"
        })
        result = asyncio.run(parse_json_response(self.logger, json_str))
        self.assertIsNotNone(result)
        self.assertIsNone(result["in-match-status"])
        #self.logger.warning.assert_any_call("Invalid 'in-match-status': INVALID, 'in-match-status' must be one of: NONE, INSTANT-REPLAY, LIVE-MATCH")
        
    def test_invalid_minimap(self):
        json_str = json.dumps({
            "match-status": "IN-MATCH",
            "in-match-status": "LIVE-MATCH",
            "minimap": "INVALID"
        })
        result = asyncio.run(parse_json_response(self.logger, json_str))
        self.assertIsNotNone(result)
        self.assertIsNone(result["minimap"])
        #self.logger.warn.assert_any_call("Invalid 'minimap': INVALID, 'minimap' must be one of: YES, NO")

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

    async def test_mk3_example_json(self):
        example_json_string = " ```json { \"match-status\": \"IN-MENU\", \"in-menu-status\": \"SQUAD-BATTLES-OPPONENT-SELECTION\" | \"UNKNOWN\", \"visible-score\": \"0-0\" } ``` "
        example_json_string = await preprocess_json_string(example_json_string)
        example_json_obj = json.loads(example_json_string)

        logger_mock = Mock(spec=logging.Logger)
        logger_mock.error = Mock()

        parsed_obj = await parse_json_response(logger_mock, example_json_string)

        self.assertIsNone(parsed_obj)
        self.assertTrue(logger_mock.error.called)

    def test_in_menu_status_returns_string(self):
        json_str = json.dumps({
            "match-status": "IN-MATCH",
            "in-match-status": "LIVE-MATCH",
            "in-menu-status": "SQUAD-BATTLES-OPPONENT-SELECTION",
            "visible-score": "0-0"
        })
        
        result = asyncio.run(parse_json_response(self.logger, json_str))
        
        in_menu_status = result.get("in-menu-status")
        
        # Assert that in_menu_status is of type str
        self.assertIsInstance(in_menu_status, str)
        
        self.assertEqual(in_menu_status, "SQUAD-BATTLES-OPPONENT-SELECTION".upper())
        
    def test_in_menu_status_returns_list(self):
        json_str_one = " ```json {     \"match-status\": \"IN-MENU\",     \"in-menu-status\": \"SQUAD-BATTLES-OPPONENT-SELECTION\" | \"UNKNOWN\",     \"visible-score\": \"0-0\" } ```  "
        # TODO: This wasn't built to support this edge case, just validate it continues to work as it does now
        json_str_two = " ```json {     \"match-status\": \"IN-MENU\",     \"in-menu-status\": \"SQUAD-BATTLES-OPPONENT-SELECTION, UNKNOWN\",     \"visible-score\": \"0-0\" } ```  "
        expected_in_menu_status = ["SQUAD-BATTLES-OPPONENT-SELECTION", "UNKNOWN"]
        
        result_one = asyncio.run(parse_json_response(self.logger, json_str_one))
        result_two = asyncio.run(parse_json_response(self.logger, json_str_two))
        
        in_menu_status_one = result_one.get("in-menu-status")
        in_menu_status_two = result_two.get("in-menu-status")

        # Assert that in_menu_status is of type list
        self.assertIsInstance(in_menu_status_one, list)
        self.assertIsInstance(in_menu_status_two, str)

        self.assertListEqual(in_menu_status_one, expected_in_menu_status)
        self.assertEqual(in_menu_status_two, "SQUAD-BATTLES-OPPONENT-SELECTION, UNKNOWN")
if __name__ == '__main__':
    unittest.main()