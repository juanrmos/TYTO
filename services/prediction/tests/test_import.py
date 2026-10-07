from pathlib import Path

import pytest
from app.services.data_pipeline import parse_monthly_csv


@pytest.mark.parametrize(
    "body",
    [
        "year,month,total_visitors\n2026,13,10\n",
        "year,month,total_visitors\n2026,1,-1\n",
        "year,month,total_visitors\n2026,1,1.5\n",
        "year,month,total_visitors\n2026,1,10\n2026,1,10\n",
        "year,month,total_visitors\n",
        "year,month\n2026,1\n",
        "year,month,total_visitors,availability_status\n2026,1,,AVAILABLE\n",
        "year,month,total_visitors,availability_status\n2026,1,1,ZERO_REPORTED\n",
        "year,month,total_visitors,availability_status\n2026,1,0,NOT_YET_AVAILABLE\n",
        "year,month,total_visitors,national_visitors,foreign_visitors\n2026,1,10,8,1\n",
    ],
)
def test_invalid_csv(tmp_path: Path, body):
    path = tmp_path / "input.csv"
    path.write_text(body, encoding="utf-8")
    with pytest.raises(ValueError):
        parse_monthly_csv(path, "TEST")


def test_missing_is_not_zero(tmp_path):
    path = tmp_path / "input.csv"
    path.write_text(
        "year,month,total_visitors,availability_status\n2026,1,,NOT_YET_AVAILABLE\n2026,2,0,ZERO_REPORTED\n",
        encoding="utf-8",
    )
    rows = parse_monthly_csv(path, "TEST")
    assert rows[0]["total_visitors"] is None and rows[1]["total_visitors"] == 0
