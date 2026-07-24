from app.tasks.jobs import process_document


def test_process_document_eager():
    result = process_document.apply(args=(1,))
    assert result.successful()
    assert result.result["document_id"] == 1
    assert result.result["status"] == "processed"
