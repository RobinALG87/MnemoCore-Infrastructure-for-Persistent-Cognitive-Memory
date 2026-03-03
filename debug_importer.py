import asyncio, json, tempfile
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock
from mnemocore.storage.memory_importer import MemoryImporter, ImportOptions, DeduplicationStrategy, ValidationLevel

async def main():
    mock = MagicMock()
    mock.upsert = AsyncMock(return_value=None)
    
    options = ImportOptions(track_imports=False)
    importer = MemoryImporter(qdrant_store=mock, default_options=options)
    
    records = [
        {"id": f"pt_{i}", "vector": [float(i)*0.1]*8, "payload": {"i": i}}
        for i in range(3)
    ]
    
    # Test _validate_record directly
    for r in records:
        valid = importer._validate_record(r, ValidationLevel.STRICT)
        print(f"Record {r['id']}: valid={valid}")
    
    # Test filter_fn
    print(f"filter_fn: {options.filter_fn}")
    print(f"track_imports: {options.track_imports}")
    print(f"deduplication: {options.deduplication}")
    print(f"validation: {options.validation}")
    
    # Now trace through _import_records manually
    imported_ids = set()
    import_log = None  # track_imports=False
    
    for record_data in records:
        rid = str(record_data.get("id", ""))
        in_set = rid in imported_ids
        print(f"  Processing {rid}: in_set={in_set}, import_log={import_log}")
        imported_ids.add(rid)
    
    print()
    
    # Now run the actual method
    imported, skipped, failed, dupes = await importer._import_records(
        "test_col", records, options, None
    )
    print(f"Results: imported={imported}, skipped={skipped}, failed={failed}, dupes={dupes}")
    
    # Also test via import_file  
    tmpdir = Path(tempfile.mkdtemp())
    json_file = tmpdir / "test.json"
    with open(json_file, "w") as f:
        json.dump(records, f)
    
    result = await importer.import_file("test_col", json_file)
    print(f"import_file result: imported={result.records_imported}, skipped={result.records_skipped}, failed={result.records_failed}")

asyncio.run(main())
