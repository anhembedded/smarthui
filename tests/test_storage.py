import pytest
import json
from unittest.mock import mock_open, patch
import storage
from storage import get_initial_data, save_data, create_default_data
from data_models import AppState

from data_models import HuiType, HuiStatus

# Arrange: A sample AppState dictionary to be used for mocking file reads
SAMPLE_APP_STATE_DICT = {
    "members": [{"id": "m1", "name": "Test Member", "phone": "123", "address": "abc", "joinDate": "2024-01-01"}],
    "groups": [{
        "id": "g1",
        "name": "Test Group",
        "members": ["m1"],
        "type": HuiType.MONTHLY.value,
        "amountPerShare": 100000,
        "commissionRate": 5,
        "totalMembers": 1,
        "startDate": "2024-01-01",
        "status": HuiStatus.ACTIVE.value,
        "currentPeriod": 1
    }],
    "transactions": [],
    "auditLogs": []
}

# Arrange: A sample AppState object for testing save operations
SAMPLE_APP_STATE_OBJ = AppState.from_dict(SAMPLE_APP_STATE_DICT)

def test_get_initial_data_loads_from_existing_file(mocker):
    """
    Test case: Verify get_initial_data loads data correctly when the file exists.
    """
    # Arrange
    mocker.patch('os.path.exists', return_value=True)
    mocked_file_content = json.dumps(SAMPLE_APP_STATE_DICT)
    mocker.patch('builtins.open', mock_open(read_data=mocked_file_content))

    # Act
    app_state = get_initial_data()

    # Assert
    assert len(app_state.members) == 1
    assert app_state.members[0].id == "m1"
    assert app_state.members[0].name == "Test Member"

def test_get_initial_data_creates_default_data_if_file_not_found(mocker):
    """
    Test case: Verify get_initial_data returns default data when the file does not exist.
    """
    # Arrange
    mocker.patch('os.path.exists', return_value=False)
    mocker.patch('storage.create_default_data', return_value=SAMPLE_APP_STATE_OBJ)

    # Act
    app_state = get_initial_data()

    # Assert
    assert app_state == SAMPLE_APP_STATE_OBJ
    storage.create_default_data.assert_called_once()

def test_get_initial_data_handles_json_decode_error(mocker):
    """
    Test case: Verify get_initial_data returns default data when the file is corrupted.
    """
    # Arrange
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('builtins.open', mock_open(read_data="invalid json"))
    mocker.patch('storage.create_default_data', return_value=SAMPLE_APP_STATE_OBJ)

    # Act
    app_state = get_initial_data()

    # Assert
    assert app_state == SAMPLE_APP_STATE_OBJ
    storage.create_default_data.assert_called_once()

def test_save_data_writes_to_file_correctly(mocker):
    """
    Test case: Verify save_data correctly serializes and writes data to the file.
    """
    # Arrange
    mock_file = mock_open()
    mocker.patch('builtins.open', mock_file)
    mocker.patch('json.dump')

    # Act
    save_data(SAMPLE_APP_STATE_OBJ)

    # Assert
    mock_file.assert_called_once_with("data.json", 'w', encoding='utf-8')
    json.dump.assert_called_once_with(
        SAMPLE_APP_STATE_OBJ.to_dict(),
        mock_file(),
        ensure_ascii=False,
        indent=2
    )

def test_create_default_data_returns_appstate():
    """
    Test case: Verify that the default data creation function returns a valid AppState object.
    """
    # Act
    default_state = create_default_data()

    # Assert
    assert isinstance(default_state, AppState)
    assert len(default_state.members) > 0
    assert len(default_state.groups) > 0
