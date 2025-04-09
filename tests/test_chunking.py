import warnings
from pathlib import Path

import pytest

import access_intake_utils
from access_intake_utils.chunking import (
    ChunkingWarning,
    get_disk_chunks,
    validate_chunkspec,
)

from .conftest import _here


def test_import():
    access_intake_utils.__file__
    assert True


@pytest.mark.parametrize(
    "fname, var, expected",
    [
        (
            str(_here / "data/output000/ocean/ocean_month.nc"),
            "mld",
            {
                "mld": {
                    "time": 1,
                    "xt_ocean": 1,
                    "yt_ocean": 1,
                },
            },
        ),
        (
            str(_here / "data/output000/ocean/ocean_month.nc"),
            ["mld", "nv"],
            {
                "mld": {
                    "time": 1,
                    "xt_ocean": 1,
                    "yt_ocean": 1,
                },
                "nv": {
                    "nv": 2,
                },
            },
        ),
        (
            str(_here / "data/output000/ocean/ocean_month.nc"),
            None,
            {
                "mld": {
                    "time": 1,
                    "xt_ocean": 1,
                    "yt_ocean": 1,
                },
                "nv": {
                    "nv": 2,
                },
                "time": {
                    "time": 120,
                },
                "time_bounds": {
                    "nv": 2,
                    "time": 1,
                },
                "xt_ocean": {
                    "xt_ocean": 1,
                },
                "yt_ocean": {
                    "yt_ocean": 1,
                },
            },
        ),
        (
            str(_here / "data/output000/ocean/ocean_month.nc"),
            "time",
            {
                "time": {
                    "time": 120,
                },
            },
        ),
    ],
)
def test_get_disk_chunks(fname, var, expected):
    fpath = Path(fname)

    assert get_disk_chunks(fpath, var) == expected


@pytest.mark.parametrize(
    "fpath, var",
    [
        (str(_here / "data/output000/ocean/ocean_month.nc"), None),
        (
            [
                str(_here / "data/output000/ocean/ocean_month.nc"),
                str(_here / "data/output001/ocean/ocean_month.nc"),
            ],
            None,
        ),
    ],
)
@pytest.mark.parametrize(
    "chunkspec, expected",
    [
        (
            {"time": 120, "xt_ocean": 1, "yt_ocean": 1, "nv": 2},
            {"time": 120, "xt_ocean": 1, "yt_ocean": 1, "nv": 2},
        ),
        (
            {"time": 120, "xt_ocean": 1, "yt_ocean": 1},
            {"time": 120, "xt_ocean": 1, "yt_ocean": 1},
        ),
        (
            {"time": 120, "xt_ocean": 1},
            {"time": 120, "xt_ocean": 1},
        ),
        (
            {"time": 120, "xt_ocean": 4},
            {"time": 120, "xt_ocean": 4},
        ),
        (
            {"time": -1, "xt_ocean": 1, "yt_ocean": 1, "nv": 2},
            {"time": -1, "xt_ocean": 1, "yt_ocean": 1, "nv": 2},
        ),
        (
            {"time": -1, "xt_ocean": 1, "yt_ocean": 1},
            {"time": -1, "xt_ocean": 1, "yt_ocean": 1},
        ),
        (
            {"time": -1, "xt_ocean": 1},
            {"time": -1, "xt_ocean": 1},
        ),
        (
            {"time": -1, "xt_ocean": 4},
            {"time": -1, "xt_ocean": 4},
        ),
    ],
)
def test_validate_chunkspec_no_warnings(
    fpath,
    chunkspec,
    var,
    expected,
):
    with warnings.catch_warnings():
        chunk_dict = validate_chunkspec(
            dataset=fpath,
            chunkspec=chunkspec,
            varnames=var,
        )

    assert chunk_dict == expected


@pytest.mark.parametrize(
    "fpath, var",
    [
        (
            Path(_here / "data/output000/ocean/ocean_month.nc"),
            None,
        ),
    ],
)
@pytest.mark.parametrize(
    "chunkspec, expected",
    [
        (
            {"time": 120, "xt_ocean": 1, "yt_ocean": 1, "nv": 1},
            {"time": 120, "xt_ocean": 1, "yt_ocean": 1, "nv": 2},
        ),
        (
            {"time": -1, "xt_ocean": 1, "yt_ocean": 1, "nv": 1},
            {"time": -1, "xt_ocean": 1, "yt_ocean": 1, "nv": 2},
        ),
        (
            {"time": 50, "xt_ocean": 1, "yt_ocean": 1, "nv": 1},
            {"time": 120, "xt_ocean": 1, "yt_ocean": 1, "nv": 2},
        ),
    ],
)
def test_validate_chunkspec_integer_multiple_warnings(
    fpath,
    chunkspec,
    var,
    expected,
):
    with pytest.warns(
        ChunkingWarning, match="Specified chunks are not integer multiples"
    ):
        chunk_dict = validate_chunkspec(
            dataset=fpath,
            chunkspec=chunkspec,
            varnames=var,
        )

    assert chunk_dict == expected


@pytest.mark.parametrize(
    "fpath, var",
    [
        (
            [
                str(_here / "data/output000/ocean/ocean_month.nc"),
                str(_here / "data/output000/ice/OUTPUT/iceh.1900-01.nc"),
            ],
            None,
        ),
    ],
)
@pytest.mark.parametrize(
    "chunkspec, expected_single, expected_multi",
    [
        (
            {"time": 120, "xt_ocean": 1, "yt_ocean": 1, "nv": 1},
            {"time": 120, "xt_ocean": 1, "yt_ocean": 1, "nv": 2},
            {
                _here / "data/output000/ocean/ocean_month.nc": {
                    "TLAT": {"ni": 1, "nj": 1},
                    "TLON": {"ni": 1, "nj": 1},
                },
                _here / "data/output000/ice/OUTPUT/iceh.1900-01.nc": {
                    "TLAT": {"ni": 1, "nj": 1},
                    "TLON": {"ni": 1, "nj": 1},
                },
            },
        ),
        (
            {"time": -1, "xt_ocean": 1, "yt_ocean": 1, "nv": 1},
            {"time": -1, "xt_ocean": 1, "yt_ocean": 1, "nv": 2},
            {
                _here / "data/output000/ocean/ocean_month.nc": {
                    "TLAT": {"ni": 1, "nj": 1},
                    "TLON": {"ni": 1, "nj": 1},
                },
                _here / "data/output000/ice/OUTPUT/iceh.1900-01.nc": {
                    "TLAT": {"ni": 1, "nj": 1},
                    "TLON": {"ni": 1, "nj": 1},
                },
            },
        ),
        (
            {"time": 50, "xt_ocean": 1, "yt_ocean": 1, "nv": 1},
            {"time": 120, "xt_ocean": 1, "yt_ocean": 1, "nv": 2},
            {
                _here / "data/output000/ocean/ocean_month.nc": {
                    "TLAT": {"ni": 1, "nj": 1},
                    "TLON": {"ni": 1, "nj": 1},
                },
                _here / "data/output000/ice/OUTPUT/iceh.1900-01.nc": {
                    "TLAT": {"ni": 1, "nj": 1},
                    "TLON": {"ni": 1, "nj": 1},
                },
            },
        ),
    ],
)
@pytest.mark.parametrize(
    "validate_mode",
    ["single", "bookend", "sample", "all", "dud"],
)
def test_validate_chunkspec_integer_different_warnings(
    fpath,
    chunkspec,
    var,
    expected_single,
    expected_multi,
    validate_mode,
):
    if validate_mode == "single":
        with warnings.catch_warnings():
            chunk_dict = validate_chunkspec(
                dataset=fpath,
                chunkspec=chunkspec,
                varnames=var,
                validate_mode=validate_mode,
            )
        assert chunk_dict == expected_single
    elif validate_mode == "dud":
        with pytest.raises(ValueError, match="Invalid validate_mode"):
            validate_chunkspec(
                dataset=fpath,
                chunkspec=chunkspec,
                varnames=var,
                validate_mode=validate_mode,
            )
        assert True
        return None
    else:
        with pytest.warns(ChunkingWarning, match="Disk chunks differ"):
            chunk_dict = validate_chunkspec(
                dataset=fpath,
                chunkspec=chunkspec,
                varnames=var,
                validate_mode=validate_mode,
            )
