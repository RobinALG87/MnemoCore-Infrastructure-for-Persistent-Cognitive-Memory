"""Test old vs new importer to find the bug."""
import asyncio, json, sys, tempfile
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

# Temporarily swap in the old code
sys.path.insert(0, "src")

from mnemocore.storage.memory_importer import (
    MemoryImporter, ImportOptions, DeduplicationStrategy, ValidationLevel
)

async def test_import():
    mock = MagicMock()
    mock.upsert = AsyncMock(return_value=None)
    
    options = ImportOptions(track_imports=False)
    importer = MemoryImporter(qdrant_store=mock, default_options=options)
    
    records = [
        {"id": f"import_point_{i:04d}", "vector": [float(i)*0.1]*128, 
         "payload": {"content": f"Import content {i}", "tier": "hot" if i%2==0 else "warm", "index": i}}
        for i in range(10)
    ]
    
    # Write to JSON file
    tmpdir = Path(tempfile.mkdtemp())
    json_file = tmpdir / "import.json"
    with open(json_file, "w") as f:
        json.dump(records, f)
    
    result = await importer.import_file("test_collection", json_file)
    
    print(f"records_processed={result.records_processed}")
    print(f"records_imported={result.records_imported}")
    print(f"records_skipped={result.records_skipped}")
    print(f"records_failed={result.records_failed}")
    print(f"duplicates_found={result.duplicates_found}")
    print(f"success={result.success}")
    
    if result.records_imported == 0 and result.records_skipped == 10:
        print("\nBUG REPRODUCED: All records skipped!")
    elif result.records_imported == 10:
        print("\nOK: All records imported.")
    else:
        print(f"\nUNEXPECTED: {result.records_imported} imported, {result.records_skipped} skipped")

asyncio.run(test_import())
