import json
import time
from pathlib import Path

import httpx
import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def async_client():
    async with httpx.AsyncClient(timeout=300.0) as client:
        yield client


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "doc_path", list(Path(__file__).parents[1].glob("demodocs/*.pdf"))
)
async def test_demodoc_vlm_processing(async_client, doc_path):
    """
    Tests the processing of a single demo document with the VLM pipeline.
    """
    base_url = "http://localhost:5001/v1"

    payload = {
        "pipeline": "vlm",
        "do_picture_description": "true",
        "picture_description_local": json.dumps(
            {"repo_id": "ds4sd/SmolDocling-256M-preview"}
        ),
        "ocr_engine": "easyocr",
        "do_ocr": "true",
        "to_formats": ["md", "json"],
        "abort_on_error": "true",
    }

    files = {"files": (doc_path.name, doc_path.open("rb"), "application/pdf")}

    print(f"Testing document: {doc_path.name}")

    # Submit the conversion task
    response = await async_client.post(
        f"{base_url}/convert/file/async", data=payload, files=files
    )
    if response.status_code != 200:
        print(response.json())
    assert response.status_code == 200, f"Failed to submit task for {doc_path.name}"
    task = response.json()
    print(f"Task submitted for {doc_path.name}: {task['task_id']}")

    # Poll for the result
    while task["task_status"] not in ("success", "failure"):
        response = await async_client.get(f"{base_url}/status/poll/{task['task_id']}")
        assert response.status_code == 200, "Polling failed"
        task = response.json()
        print(
            f"Task status for {doc_path.name}: {task['task_status']} ({task.get('task_position', 'N/A')})"
        )
        time.sleep(5)

    assert task["task_status"] == "success", f"Task failed for {doc_path.name}"
    print(f"Task for {doc_path.name} completed successfully.")

    # Get the result
    result_resp = await async_client.get(f"{base_url}/result/{task['task_id']}")
    assert result_resp.status_code == 200, "Failed to get result"
    result = result_resp.json()

    # Define output paths
    output_dir = Path(__file__).parent / "test_output"
    md_output_path = output_dir / f"{doc_path.stem}.md"
    json_output_path = output_dir / f"{doc_path.stem}.json"

    # Save the results
    md_content = result.get("document", {}).get("md_content", "")
    json_content = result.get("document", {}).get("json_content", {})

    with open(md_output_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Saved markdown to {md_output_path}")

    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(json_content, f, indent=2)
    print(f"Saved json to {json_output_path}")

    # Verify the result
    assert "document" in result
    doc = result["document"]
    assert "md_content" in doc and doc["md_content"]
    assert "json_content" in doc and doc["json_content"]
    assert doc["json_content"]["schema_name"] == "DoclingDocument"

    print(f"Successfully verified results for {doc_path.name}")
