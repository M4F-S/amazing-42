import sys
from unittest.mock import patch

import pytest

from a_maze_ing import main


def test_end_to_end_maze_generation(tmp_path):
    """Test the complete workflow from parsing config to generating and writing the maze.
    
    This patches `sys.argv` to point to a temporary test configuration, and
    mocks the interactive `run_cli` UI loop so the test doesn't block waiting for input.
    """
    config_path = tmp_path / "config.txt"
    output_path = tmp_path / "maze_output.txt"

    # Create a valid test configuration
    config_content = f"""
    WIDTH=15
    HEIGHT=15
    ENTRY=0,0
    EXIT=14,14
    OUTPUT_FILE={output_path}
    PERFECT=True
    SEED=42
    """
    config_path.write_text(config_content.strip())

    # Execute main() while mocking the CLI
    with patch.object(sys, "argv", ["a_maze_ing.py", str(config_path)]):
        with patch("a_maze_ing.run_cli") as mock_run_cli:
            exit_code = main()

    # Verify normal exit
    assert exit_code == 0

    # Verify run_cli was reached and called once
    assert mock_run_cli.called
    assert mock_run_cli.call_count == 1

    # Verify the output file was successfully written to the filesystem
    assert output_path.exists()

    # Do a basic sanity check on the output file formatting
    output_content = output_path.read_text()
    
    # Check that entry and exit coordinates were properly written to the file
    assert "0,0" in output_content
    assert "14,14" in output_content
    
    # Path coordinates string should exist on the last line or close to it
    lines = output_content.strip().split("\n")
    # File format: <hex_grid> ... <blank> ... <entry> ... <exit> ... <path>
    assert len(lines) > 15
