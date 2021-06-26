from datetime import datetime, timedelta

from files.bruteforce import BruteForce
from files.logs import Logs
from freezegun import freeze_time


def test_create():
    brute_force = BruteForce(False, 60, 1)
    assert len(brute_force.database) == 0
    assert not brute_force.enabled
    assert brute_force.expiration_in_seconds == 60
    assert brute_force.block_after_failures == 1
    assert isinstance(brute_force.logs, Logs)


def test_failure_is_not_added_if_disabled():
    brute_force = BruteForce(False, 1, 1)
    assert len(brute_force.database) == 0
    brute_force.add_failure('some ip address')
    assert len(brute_force.database) == 0


@freeze_time('2021-06-25 21:06:30')
def test_add_first_ip_to_db(capsys):
    ip_address = '127.0.0.1'
    expected_log = '2021-06-25 21:06:30 - INFO - BruteForce - ' \
                   f'{ip_address} -  - Start IP failure counter. - 1\n'
    brute_force = BruteForce(True, 1, 1)
    brute_force.add_failure(ip_address)
    ip_entry = brute_force.database[ip_address]

    assert str(ip_entry['blockUntil']) == '2021-06-25 21:06:31'
    assert ip_entry['counter'] == 1
    assert capsys.readouterr().out == expected_log


@freeze_time('2021-06-25 21:06:30')
def test_expire_and_renew_ip_in_db(capsys):
    expected_msg = 'IP failure counter expired, removing IP...'
    ip_address = '127.0.0.1'
    brute_force = BruteForce(True, 1, 3)
    brute_force.add_failure(ip_address)

    entry = brute_force.database[ip_address]
    entry['blockUntil'] = datetime.now() - timedelta(seconds=1)
    assert entry['counter'] == 1

    brute_force.add_failure(ip_address)
    assert entry != brute_force.database[ip_address]
    assert brute_force.database[ip_address]['counter'] == 1
    assert expected_msg in capsys.readouterr().out


@freeze_time('2021-06-25 21:06:30')
def test_add_ip_and_increase_failure_counter(capsys):
    ip_address = '127.0.0.1'
    brute_force = BruteForce(True, 1, 3)
    brute_force.add_failure(ip_address)
    assert brute_force.database[ip_address]['counter'] == 1

    brute_force.add_failure(ip_address)
    assert brute_force.database[ip_address]['counter'] == 2
    assert 'Increase IP failure counter' in capsys.readouterr().out


@freeze_time('2021-06-25 21:06:30')
def test_add_ip_and_block(capsys):
    new_time = datetime.now() + timedelta(seconds=1)
    ip_address = '127.0.0.1'
    brute_force = BruteForce(True, 20, 2)
    brute_force.add_failure(ip_address)
    entry = brute_force.database[ip_address]
    entry['blockUntil'] = new_time

    assert entry['counter'] == 1

    brute_force.add_failure(ip_address)
    assert entry['counter'] == 2
    assert entry['blockUntil'] != new_time
    assert str(entry['blockUntil']) == '2021-06-25 21:06:50'
    assert 'IP blocked.' in capsys.readouterr().out


def test_ip_block_is_not_checked_if_disabled():
    brute_force = BruteForce(False, 1, 1)
    assert not brute_force.is_ip_blocked('some ip address')


def test_new_ip_is_not_blocked(capsys):
    brute_force = BruteForce(True, 1, 1)
    assert not brute_force.is_ip_blocked('127.0.0.1')
    assert 'The IP is not in the database and is not blocked.' in capsys.readouterr().out


def test_ip_is_not_blocked(capsys):
    brute_force = BruteForce(True, 1, 2)
    brute_force.add_failure('127.0.0.1')
    assert not brute_force.is_ip_blocked('127.0.0.1')
    assert 'The IP is not blocked.' in capsys.readouterr().out


@freeze_time('2021-06-25 21:06:30')
def test_ip_is_blocked(capsys):
    brute_force = BruteForce(True, 1, 1)
    brute_force.add_failure('127.0.0.1')
    assert brute_force.is_ip_blocked('127.0.0.1')
    assert 'The IP is blocked.' in capsys.readouterr().out


@freeze_time('2021-06-25 21:06:30')
def test_ip_block_expired(capsys):
    new_time = datetime.now() - timedelta(seconds=1)
    brute_force = BruteForce(True, 1, 1)
    brute_force.add_failure('127.0.0.1')
    brute_force.database['127.0.0.1']['blockUntil'] = new_time

    assert not brute_force.is_ip_blocked('127.0.0.1')

    out = capsys.readouterr().out
    assert 'The IP is blocked.' in out
    assert 'Removing IP from the database, lucky guy, time expired.' in out
