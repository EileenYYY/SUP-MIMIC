from mimic_pipeline_kit.analysis.comparison import standardized_mean_difference
from mimic_pipeline_kit.analysis.descriptive import summarize_records


def test_summarize_records_numeric_fields():
    rows = [{"x": 1, "y": 2}, {"x": 3, "y": 4}]
    summary = summarize_records(rows)
    assert summary["n"] == 2
    assert summary["fields"]["x"]["mean"] == 2.0
    assert summary["fields"]["y"]["max"] == 4.0


def test_standardized_mean_difference_basic():
    smd = standardized_mean_difference([1, 2, 3], [2, 3, 4])
    assert smd is not None

