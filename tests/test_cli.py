"""The command line's shared pieces read the same from every package."""

import dataclasses
import json

import pytest

from strata.common.cli import emit, exit_on, jsonable, run
from strata.common.errors import Refused, SchemaOutOfDate


@dataclasses.dataclass
class Record:
    made: str
    left_out: dict[str, int]


def test_json_goes_to_stdout_whole_and_nothing_else(capsys):
    emit(Record("v3", {"unreadable": 2}), lambda r: [f"made {r.made}"], as_json=True)
    out, err = capsys.readouterr()
    assert json.loads(out) == {"left_out": {"unreadable": 2}, "made": "v3"}
    assert err == ""


def test_a_person_gets_the_rendering(capsys):
    emit(Record("v3", {}), lambda r: [f"made {r.made}"], as_json=False)
    assert capsys.readouterr().out == "made v3\n"


def test_jsonable_takes_models_dataclasses_and_their_collections():
    class Model:
        def model_dump(self, mode):
            return {"a": 1}

    assert jsonable([Model(), Record("x", {})]) == [{"a": 1}, {"made": "x", "left_out": {}}]
    assert jsonable({"k": (1, 2)}) == {"k": [1, 2]}


def test_run_turns_a_named_refusal_into_one_line_and_status_1(capsys):
    class Mine(Exception):
        pass

    def body():
        raise Mine("no catalog at /x")

    assert run(body, Mine) == 1
    out, err = capsys.readouterr()
    assert (out, err) == ("", "no catalog at /x\n")


def test_run_always_refuses_a_store_behind_the_code_and_a_refusal(capsys):
    def behind():
        raise SchemaOutOfDate("at r1, code expects r2")

    def refused():
        raise Refused("stop")

    assert run(behind) == 1
    assert run(refused) == 1
    assert capsys.readouterr().err == "at r1, code expects r2\nstop\n"


def test_run_returns_the_status_and_lets_a_crash_through():
    assert run(lambda: None) == 0
    assert run(lambda: 3) == 3
    with pytest.raises(KeyError):
        run(lambda: {}["x"])


def test_exit_on_exits_with_status_1_for_a_named_refusal(capsys):
    with pytest.raises(SystemExit) as stop, exit_on(ValueError):
        raise ValueError("bad --set")
    assert stop.value.code == 1
    assert capsys.readouterr().err == "bad --set\n"


def test_exit_on_lets_a_crash_through():
    with pytest.raises(KeyError), exit_on(ValueError):
        raise KeyError("x")
