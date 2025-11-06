from datetime import datetime
from pyepidoc.tei.metadata.change import Change

def test_change_uses_todays_date_when_date_not_provided():
    # Act
    change = Change.from_details("#RC")

    # Assert
    assert change.when == datetime.today().strftime('%Y-%m-%d')