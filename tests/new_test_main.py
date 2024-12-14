import pytest
import requests
from datetime import datetime
from unittest.mock import Mock, patch
from src.main import process_outages, KrakenFlexAPI, main


def test_process_outages():
    """Test the process_outages function with valid data."""
    # Mock API client
    mock_client = Mock()
    
    # Mock outage data
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
    
    # Mock site info
    mock_client.get_site_info.return_value = {
        "id": "test-site",
        "devices": [
            {
                "id": "002b28fc-283c-47ec-9af2-ea287336dc1b",
                "name": "Test Device"
            }
        ]
    }
    
    # Call the function
    result = process_outages(mock_client, 'test-site')
    
    # Assertions
    assert len(result) == 1
    assert result[0]['name'] == 'Test Device'
    assert datetime.fromisoformat(result[0]['begin'].replace('Z', '')).replace(tzinfo=None) >= datetime(2022, 1, 1)


def test_process_outages_no_devices():
    """Test process_outages with a site that has no devices."""
    mock_client = Mock()
    mock_client.get_outages.return_value = [
        {
            "id": "abc123",
            "begin": "2022-05-01T12:00:00Z",
            "end": "2022-05-02T12:00:00Z"
        }
    ]
    mock_client.get_site_info.return_value = {"id": "test-site", "devices": []}

    result = process_outages(mock_client, "test-site")
    assert len(result) == 0


def test_krakenflexapi_get_outages():
    """Test the get_outages method of KrakenFlexAPI."""
    mock_response = [{"id": "outage1", "begin": "2022-05-01T12:00:00Z", "end": "2022-05-02T12:00:00Z"}]
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.status_code = 200

        api = KrakenFlexAPI("test-api-key")
        result = api.get_outages()
        assert result == mock_response


def test_krakenflexapi_post_site_outages():
    """Test the post_site_outages method of KrakenFlexAPI."""
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"status": "success"}

        api = KrakenFlexAPI("test-api-key")
        response = api.post_site_outages("test-site", [{"id": "abc123"}])
        assert response == {"status": "success"}


def test_retry_logic_in_make_request():
    """Test the retry logic in the _make_request method."""
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        api = KrakenFlexAPI("test-api-key")

        with pytest.raises(Exception):
            api._make_request("get", "outages")


@patch("os.getenv")
@patch("src.main.process_outages")
@patch("src.main.KrakenFlexAPI")
def test_main(mock_api_class, mock_process_outages, mock_getenv):
    """Test the main function end-to-end."""
    mock_getenv.side_effect = lambda key, default=None: {
        "KRAKENFLEX_API_KEY": "test-api-key",
        "SITE_ID": "test-site"
    }.get(key, default)

    mock_instance = mock_api_class.return_value
    mock_process_outages.return_value = [{"id": "abc123", "begin": "2022-01-01T00:00:00Z"}]
    mock_instance.post_site_outages.return_value = {"status": "success"}

    main()

    mock_process_outages.assert_called_once_with(mock_instance, "test-site")
    mock_instance.post_site_outages.assert_called_once_with("test-site", [{"id": "abc123", "begin": "2022-01-01T00:00:00Z"}])
