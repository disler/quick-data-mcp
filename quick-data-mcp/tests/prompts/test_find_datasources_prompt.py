"""Tests for find_datasources prompt functionality."""

import pytest
import tempfile
import os
import json
import pandas as pd
from pathlib import Path

from mcp_server.prompts.find_datasources_prompt import find_datasources, format_file_size


class TestFindDatasources:
    """Test find_datasources prompt functionality."""
    
    @pytest.mark.asyncio
    async def test_find_datasources_with_files(self):
        """Test finding data sources in a directory with CSV and JSON files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create sample CSV file
            csv_data = {'id': [1, 2, 3], 'name': ['A', 'B', 'C']}
            csv_file = temp_path / "sample_data.csv"
            pd.DataFrame(csv_data).to_csv(csv_file, index=False)
            
            # Create sample JSON file
            json_data = [{'id': 1, 'value': 100}, {'id': 2, 'value': 200}]
            json_file = temp_path / "test_data.json"
            with open(json_file, 'w') as f:
                json.dump(json_data, f)
            
            result = await find_datasources(str(temp_path))
            
            assert isinstance(result, str)
            assert "Data Source Discovery" in result
            assert "sample_data.csv" in result
            assert "test_data.json" in result
            assert "load_dataset" in result
            assert "sample_data" in result  # Suggested dataset name
            assert "test_data" in result   # Suggested dataset name
            assert "CSV" in result
            assert "JSON" in result
    
    @pytest.mark.asyncio
    async def test_find_datasources_with_subdirectories(self):
        """Test finding data sources in subdirectories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create data subdirectory
            data_dir = temp_path / "data"
            data_dir.mkdir()
            
            # Create file in subdirectory
            csv_data = {'x': [1, 2], 'y': [3, 4]}
            csv_file = data_dir / "subdir_data.csv"
            pd.DataFrame(csv_data).to_csv(csv_file, index=False)
            
            result = await find_datasources(str(temp_path))
            
            assert isinstance(result, str)
            assert "Data Source Discovery" in result
            assert "data/ directory" in result
            assert "subdir_data.csv" in result
            assert "load_dataset" in result
    
    @pytest.mark.asyncio
    async def test_find_datasources_no_files(self):
        """Test behavior when no data files are found."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a text file (not CSV/JSON)
            text_file = Path(temp_dir) / "readme.txt"
            text_file.write_text("This is not a data file")
            
            result = await find_datasources(temp_dir)
            
            assert isinstance(result, str)
            assert "No data files found" in result
            assert "Suggestions:" in result
            assert "Manual file search:" in result
    
    @pytest.mark.asyncio
    async def test_find_datasources_current_directory(self):
        """Test finding data sources in current directory (default behavior)."""
        # Test with default parameter (current directory)
        result = await find_datasources()
        
        assert isinstance(result, str)
        assert "Data Source Discovery" in result
        # Should not error out, even if no files found
        assert ("Data files found" in result or "No data files found" in result)
    
    @pytest.mark.asyncio
    async def test_find_datasources_nonexistent_directory(self):
        """Test handling for non-existent directory."""
        result = await find_datasources("/nonexistent/directory/path")
        
        assert isinstance(result, str)
        # Non-existent directory should be handled gracefully
        assert ("No data files found" in result or "Error discovering data sources" in result)
        assert "Manual file search:" in result
    
    @pytest.mark.asyncio
    async def test_find_datasources_file_size_formatting(self):
        """Test that file sizes are properly formatted."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create a larger CSV file
            large_data = {'col' + str(i): list(range(100)) for i in range(10)}
            csv_file = temp_path / "large_data.csv"
            pd.DataFrame(large_data).to_csv(csv_file, index=False)
            
            result = await find_datasources(str(temp_path))
            
            assert isinstance(result, str)
            assert "large_data.csv" in result
            # Should have file size information
            assert ("KB" in result or "MB" in result or "B" in result)
    
    @pytest.mark.asyncio
    async def test_find_datasources_special_characters_in_filename(self):
        """Test handling of files with special characters in names."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create file with spaces and hyphens
            csv_data = {'a': [1, 2], 'b': [3, 4]}
            csv_file = temp_path / "My Data-File.csv"
            pd.DataFrame(csv_data).to_csv(csv_file, index=False)
            
            result = await find_datasources(str(temp_path))
            
            assert isinstance(result, str)
            assert "My Data-File.csv" in result
            # Should suggest cleaned up dataset name
            assert "my_data_file" in result


class TestFormatFileSize:
    """Test format_file_size utility function."""
    
    def test_format_file_size_bytes(self):
        """Test formatting file sizes in bytes."""
        assert format_file_size(0) == "0 B"
        assert format_file_size(512) == "512 B"
        assert format_file_size(1023) == "1023 B"
    
    def test_format_file_size_kilobytes(self):
        """Test formatting file sizes in kilobytes."""
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(2048) == "2.0 KB"
        assert format_file_size(1536) == "1.5 KB"
    
    def test_format_file_size_megabytes(self):
        """Test formatting file sizes in megabytes."""
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(1024 * 1024 * 2.5) == "2.5 MB"
    
    def test_format_file_size_gigabytes(self):
        """Test formatting file sizes in gigabytes."""
        assert format_file_size(1024 * 1024 * 1024) == "1.0 GB"
        assert format_file_size(1024 * 1024 * 1024 * 1.5) == "1.5 GB"


if __name__ == '__main__':
    pytest.main([__file__])