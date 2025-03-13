from pyepidoc.analysis.utils.division import Division


def test_division_eval():

    # Arrange
    div = Division(10, 2)

    # Act
    value = div.value

    # Assert
    assert value == 5.0


def test_division_percentage():
    # Arrange
    div = Division(2, 10)

    # Act
    pc = div.percentage()

    # Assert
    assert pc == 20.00