import pytest
from datetime import datetime
from unittest.mock import Mock
from src.main import process_outages, main

def test_process_outages():
    # Mock API client
    mock_client = Mock()
    
    # Sample outage data
    mock_client.get_outages.return_value = [
        {
            "id": "002b28fc-283c-47ec-9af2-ea287336dc1b",
            "begin": "2022-05-23T12:21:27.377Z",
            "end": "2022-11-13T02:16:38.905Z"
        },
        {
            "id": "027e4a6b-mock-older-outage",
            "begin": "2021-01-01T00:00:00.000Z",
            "end": "2021-02-01T00:00:00.000Z"
        }
    ]
    
    # Sample site info
    mock_client.get_site_info.return_value = {
        "id": "test-site",
        "devices": [
            {
                "id": "002b28fc-283c-47ec-9af2-ea287336dc1b",
                "name": "Test Device"
            }
        ]
    }
    
    # Process outages
    result = process_outages(mock_client, 'test-site')
    
    # Assertions
    assert len(result) == 1
    assert result[0]['name'] == 'Test Device'
    assert datetime.fromisoformat(result[0]['begin'].replace('Z', '')).replace(tzinfo=None) >= datetime(2022, 1, 1)
