import os
from unittest import mock

import pytest
from freezegun import freeze_time
from files.logs import Logs


def test_create_default():
    obj_name = 'foo'
    logs = Logs(obj_name)
    assert logs.level == 'INFO'
    assert logs.format == 'TEXT'
    assert logs.object_name == obj_name


def _create_logs_with_env(level: str, log_format: str) -> Logs:
    d = {'LOG_LEVEL': level, 'LOG_FORMAT': log_format}
    with mock.patch.dict(os.environ, d):
        return Logs('test')


@pytest.mark.parametrize('log_level', ['INFO', 'WARNING', 'ERROR'])
@pytest.mark.parametrize('log_format', ['JSON', 'TEXT'])
def test_create_with_environ(log_level: str, log_format: str):
    logs = _create_logs_with_env(log_level, log_format)
    assert logs.level == log_level
    assert logs.format == log_format


@freeze_time('2021-06-25 21:06:30')
@pytest.mark.parametrize(
    'level, log_format, expected',
    [
        ('INFO', 'TEXT', '2021-06-25 21:06:30 - INFO - test -  -  - msg\n'),
        ('WARNING', 'TEXT', ''),
        ('ERROR', 'TEXT', ''),
        ('INFO', 'JSON', '{"date": "2021-06-25 21:06:30", "level": "INFO",'
                         ' "objectName": "test", "ip": "", "referrer": "", '
                         '"message": "msg"}\n'),
        ('WARNING', 'JSON', ''),
        ('ERROR', 'JSON', '')
    ]
)
def test_print_info_level(level, log_format, expected, capsys):
    logs = _create_logs_with_env(level, log_format)
    logs.info({'message': 'msg'})
    assert capsys.readouterr().out == expected


@freeze_time('2021-06-25 21:06:30')
@pytest.mark.parametrize(
    'level, log_format, expected',
    [
        ('INFO', 'TEXT', '2021-06-25 21:06:30 - WARNING - test -  -  - msg\n'),
        ('WARNING', 'TEXT',
         '2021-06-25 21:06:30 - WARNING - test -  -  - msg\n'),
        ('ERROR', 'TEXT', ''),
        ('INFO', 'JSON', '{"date": "2021-06-25 21:06:30", "level": "WARNING",'
                         ' "objectName": "test", "ip": "", "referrer": "", '
                         '"message": "msg"}\n'),
        ('WARNING', 'JSON', '{"date": "2021-06-25 21:06:30", '
                            '"level": "WARNING", "objectName": '
                            '"test", "ip": "", "referrer": "", '
                            '"message": "msg"}\n'),
        ('ERROR', 'JSON', '')
    ]
)
def test_print_warning_level(level, log_format, expected, capsys):
    logs = _create_logs_with_env(level, log_format)
    logs.warning({'message': 'msg'})
    assert capsys.readouterr().out == expected


@freeze_time('2021-06-25 21:06:30')
@pytest.mark.parametrize(
    'level, log_format, expected',
    [
        ('INFO', 'TEXT', '2021-06-25 21:06:30 - ERROR - test -  -  - msg\n'),
        ('WARNING', 'TEXT', '2021-06-25 21:06:30 - ERROR - test -  -  - msg\n'),
        ('ERROR', 'TEXT', '2021-06-25 21:06:30 - ERROR - test -  -  - msg\n'),
        ('INFO', 'JSON', '{"date": "2021-06-25 21:06:30", "level": "ERROR",'
                         ' "objectName": "test", "ip": "", "referrer": "", '
                         '"message": "msg"}\n'),
        ('WARNING', 'JSON', '{"date": "2021-06-25 21:06:30", '
                            '"level": "ERROR", "objectName": '
                            '"test", "ip": "", "referrer": "", '
                            '"message": "msg"}\n'),
        ('ERROR', 'JSON', '{"date": "2021-06-25 21:06:30", '
                          '"level": "ERROR", "objectName": '
                          '"test", "ip": "", "referrer": "", '
                          '"message": "msg"}\n'),
    ]
)
def test_print_error_level(level, log_format, expected, capsys):
    logs = _create_logs_with_env(level, log_format)
    logs.error({'message': 'msg'})
    assert capsys.readouterr().out == expected
