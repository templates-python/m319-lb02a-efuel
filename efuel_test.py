import dataclasses
import json
import random
from datetime import datetime

import pytest

import efuel as efuel
from entry import Entry


def test_setup(monkeypatch, capsys, test_values):
    if isinstance(test_values, dict) and \
            isinstance(test_values['energy_price'], float) and \
            isinstance(test_values['client1'], str) and \
            isinstance(test_values['client2'], str) and \
            isinstance(test_values['client3'], str):
        print('\tSetup erfolgreich')
    else:
        pytest.fail('\tDie Datei "testdata.json" fehlt oder ist fehlerhaft. Kontaktieren Sie Ihre Lehrperson.')


def test_attributes(monkeypatch, capsys, attributes):
    if attributes not in ['BASIS', 'ERWEITERT']:
        pytest.fail('Attribute in Entry sind falsch oder fehlen; Test kann nicht durchgeführt werden')

    energy = random.randint(19, 95) / 10
    if attributes == 'BASIS':
        start = '26.02.2023 06:00'
        end = '26.02.2023 08:30'
        release = '26.02.2023 09:45'
    else:
        start = datetime.strptime('26.02.2023 06:00', '%d.%m.%Y %H:%M')
        end = datetime.strptime('26.02.2023 08:30', '%d.%m.%Y %H:%M')
        release = datetime.strptime('26.02.2023 09:45', '%d.%m.%Y %H:%M')
    entry = Entry(start, end, release, energy)
    assert dataclasses.astuple(entry) == (start, end, release, energy)


def test_cost1(monkeypatch, capsys, attributes, test_values):
    if attributes not in ['BASIS', 'ERWEITERT']:
        pytest.fail('Attribute in Entry sind falsch oder fehlen; Test kann nicht durchgeführt werden')

    energy = random.randint(50, 199) / 10
    if attributes == 'BASIS':
        start = '23.01.2023 12:00'
        end = '23.01.2023 12:30'
        release = '23.01.2023 12:40'
    else:
        start = datetime.strptime('23.01.2023 12:00', '%d.%m.%Y %H:%M')
        end = datetime.strptime('23.01.2023 12:30', '%d.%m.%Y %H:%M')
        release = datetime.strptime('23.01.2023 12:40', '%d.%m.%Y %H:%M')
    entry = Entry(start, end, release, energy)
    assert entry.cost == round((energy * test_values['energy_price']), 2)


def test_cost2(monkeypatch, capsys, attributes, test_values):
    if attributes != 'ERWEITERT':
        pytest.fail('Test kann nur mit den Attributen der Version ERWEITERT durchgeführt werden')

    energy = random.randint(10, 399) / 10
    start = datetime.strptime('09.01.2023 12:00', '%d.%m.%Y %H:%M')
    end = datetime.strptime('09.01.2023 12:30', '%d.%m.%Y %H:%M')
    release = datetime.strptime('09.01.2023 13:15', '%d.%m.%Y %H:%M')
    entry = Entry(start, end, release, energy)
    assert entry.cost == round((energy * test_values['energy_price'] + 30 * 0.05), 2)


def test_init_accounts1(monkeypatch, capsys, collection, test_values):
    if collection not in ['BASIS', 'ERWEITERT']:
        pytest.fail('Test kann erst durchgeführt werden, wenn init_accounts() korrekt läuft')

    if collection == 'BASIS':
        assert efuel.init_accounts() == list()
    elif collection == 'ERWEITERT':
        collection = efuel.init_accounts()
        assert test_values['client1'] in collection


def test_init_accounts2(monkeypatch, capsys, collection, test_values):
    if collection != 'ERWEITERT':
        pytest.fail('Test kann nur mit der erweiterten Version von init_accounts() ausgeführt werden')

    collection = efuel.init_accounts()
    client = test_values['client2']
    assert collection[client] == []


def test_read_entry(monkeypatch, capsys, attributes):
    if attributes not in ['BASIS', 'ERWEITERT']:
        pytest.fail('Test kann erst durchgeführt werden, wenn die Attribute der Klasse "Entry" definiert sind')

    energy = random.randint(50, 79) / 10
    inputs = iter(['06.01.2023 08:07', '06.01.2023 09:45', '06.01.2023 10:00', energy])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    entry = efuel.read_entry()
    if attributes == 'BASIS':
        assert entry == Entry('06.01.2023 08:07', '06.01.2023 09:45', '06.01.2023 10:00', energy)
    else:
        assert entry == Entry(
            datetime.strptime('06.01.2023 08:07', '%d.%m.%Y %H:%M'),
            datetime.strptime('06.01.2023 09:45', '%d.%m.%Y %H:%M'),
            datetime.strptime('06.01.2023 10:00', '%d.%m.%Y %H:%M'),
            energy
        )


def test_add_entries1(monkeypatch, capsys, collection, test_values):
    if collection not in ['BASIS', 'ERWEITERT']:
        pytest.fail('Test kann erst durchgeführt werden, wenn init_accounts() korrekt läuft')

    energy = random.randint(80, 150) / 10
    accounts = efuel.init_accounts()
    if collection == 'BASIS':
        inputs = iter(['06.01.2023 08:07', '06.01.2023 09:45', '06.01.2023 10:00', energy, 'y'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        efuel.add_entries(accounts)
        assert isinstance(accounts[0], Entry)
    elif collection == 'ERWEITERT':
        client = test_values['client3']
        inputs = iter([client, '06.01.2023 08:07', '06.01.2023 09:45', '06.01.2023 10:00', energy, 'y'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        efuel.add_entries(accounts)
        entry = accounts[client][0]
        assert isinstance(entry, Entry)


def test_add_entries2(monkeypatch, capsys, collection, test_values):
    if collection != 'ERWEITERT':
        pytest.fail('Test kann nur mit der erweiterten Version (dict) durchgeführt werden')

    inputs = iter([
        test_values['client1'], '06.01.2023 08:07', '06.01.2023 09:45', '06.01.2023 10:00', 57.5, 'n',
        test_values['client2'], '10.01.2023 13:15', '10.01.2023 14:20', '10.01.2023 14:21', 13, 'n',
        test_values['client1'], '12.01.2023 08:00', '12.01.2023 09:00', '12.01.2023 10:00', 57.5, 'y'
    ])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    collection = {test_values['client1']: list(), test_values['client2']: list(), test_values['client3']: list()}
    efuel.add_entries(collection)
    assert isinstance(collection[test_values['client1']][1], Entry)


def test_show_balance1(monkeypatch, capsys, collection, attributes, test_values):
    if attributes not in ['BASIS', 'ERWEITERT']:
        pytest.fail('Attribute in Entry sind falsch oder fehlen; Test kann nicht durchgeführt werden')
    elif collection not in ['BASIS', 'ERWEITERT']:
        pytest.fail('Test kann erst durchgeführt werden, wenn init_accounts() korrekt läuft')

    if attributes == 'BASIS':
        entry1 = Entry(
            '12.03.2023 15:17',
            '12.03.2023 17:43',
            '12.03.2023 17:56',
            57.5
        )
        entry2 = Entry(
            '21.03.2023 08:04',
            '21.03.2023 09:53',
            '21.03.2023 10:05',
            31.35
        )
    else:
        entry1 = Entry(
            datetime.strptime('12.03.2023 15:17', '%d.%m.%Y %H:%M'),
            datetime.strptime('12.03.2023 17:43', '%d.%m.%Y %H:%M'),
            datetime.strptime('12.03.2023 17:56', '%d.%m.%Y %H:%M'),
            57.5
        )
        entry2 = Entry(
            datetime.strptime('21.03.2023 08:04', '%d.%m.%Y %H:%M'),
            datetime.strptime('21.03.2023 09:53', '%d.%m.%Y %H:%M'),
            datetime.strptime('21.03.2023 10:05', '%d.%m.%Y %H:%M'),
            31.35
        )

    if attributes == 'BASIS' and collection == 'BASIS':
        cost0 = round((57.5 * test_values['energy_price']), 2)
        cost1 = round((31.35 * test_values['energy_price']), 2)
        output = '  {sign} 12.03.2023 15:17\tCHF {amount0:.2f}\n' \
                 '  {sign} 21.03.2023 08:04\tCHF {amount1:.2f}\n' \
                 '{total:<20}\tCHF {amount2:.2f}\n' \
            .format(
            sign='-',
            total='Summe:',
            amount0=cost0,
            amount1=cost1,
            amount2=(cost0 + cost1)
        )
        accounting = [entry1, entry2]
        efuel.show_balance(accounting)
        captured = capsys.readouterr()
        assert captured.out == output
    elif attributes == 'ERWEITERT' and collection == 'ERWEITERT':
        cost0 = round((57.5 * test_values['energy_price']), 2)
        cost1 = round((31.35 * test_values['energy_price']), 2)
        output = 'Abrechnung für {client}\n' \
                 '  {sign} 12.03.2023 15:17\tCHF {amount0:.2f}\n' \
                 '  {sign} 21.03.2023 08:04\tCHF {amount1:.2f}\n' \
                 '{total:<20}\tCHF {amount2:.2f}\n' \
            .format(
            client=test_values['client2'],
            sign='-',
            total='Summe:',
            amount0=cost0,
            amount1=cost1,
            amount2=(cost0 + cost1)
        )
        accounting = {test_values['client2']: [entry1, entry2]}
        efuel.show_balance(accounting)
        captured = capsys.readouterr()
        assert captured.out == output
    elif attributes == 'ERWEITERT' and collection == 'BASIS':
        cost0 = round((57.5 * test_values['energy_price']), 2)
        cost1 = round((31.35 * test_values['energy_price']), 2)
        output = '  {sign} 2023-03-12 15:17:00\tCHF {amount0:.2f}\n' \
                 '  {sign} 2023-03-21 08:04:00\tCHF {amount1:.2f}\n' \
                 '{total:<20}\tCHF {amount2:.2f}\n' \
            .format(
            sign='-',
            total='Summe:',
            amount0=cost0,
            amount1=cost1,
            amount2=(cost0 + cost1)
        )
        accounting = [entry1, entry2]
        efuel.show_balance(accounting)
        captured = capsys.readouterr()
        assert captured.out == output


def test_show_balance2(monkeypatch, capsys, collection, test_values):
    if collection != 'ERWEITERT':
        pytest.fail('Test kann nur mit der erweiterten Version von init_accounts() durchgeführt werden')

    entry1 = Entry(
        datetime.strptime('12.03.2023 15:17', '%d.%m.%Y %H:%M'),
        datetime.strptime('12.03.2023 17:43', '%d.%m.%Y %H:%M'),
        datetime.strptime('12.03.2023 22:16', '%d.%m.%Y %H:%M'),
        57.5
    )
    entry2 = Entry(
        datetime.strptime('21.03.2023 08:04', '%d.%m.%Y %H:%M'),
        datetime.strptime('21.03.2023 09:53', '%d.%m.%Y %H:%M'),
        datetime.strptime('21.03.2023 10:05', '%d.%m.%Y %H:%M'),
        31.35
    )
    entry3 = Entry(
        datetime.strptime('12.03.2023 06:02', '%d.%m.%Y %H:%M'),
        datetime.strptime('12.03.2023 07:41', '%d.%m.%Y %H:%M'),
        datetime.strptime('12.03.2023 08:37', '%d.%m.%Y %H:%M'),
        61.75
    )
    cost0 = round((57.5 * test_values['energy_price'] + 258 * 0.05), 2)
    cost1 = round((31.35 * test_values['energy_price']), 2)
    cost2 = cost0 + cost1
    cost3 = round((61.75 * test_values['energy_price'] + 41 * 0.05), 2)
    accounting = {
        test_values['client1']: [entry1, entry2],
        test_values['client2']: [entry3]
    }
    output = 'Abrechnung für {client1}\n' \
             '  {sign} 12.03.2023 15:17:\tCHF {amount0:.2f}\n' \
             '  {sign} 21.03.2023 08:04:\tCHF {amount1:.2f}\n' \
             '{total:<20}\tCHF {amount2:.2f}\n' \
             'Abrechnung für {client2}\n' \
             '  {sign} 12.03.2023 06:02:\tCHF {amount3:.2f}\n' \
             '{total:<20}\tCHF {amount3:.2f}\n' \
        .format(
        sign='-',
        total='Summe:',
        client1=test_values['client1'],
        client2=test_values['client2'],
        amount0=cost0,
        amount1=cost1,
        amount2=cost2,
        amount3=cost3
    )
    try:
        efuel.show_balance(accounting)
        captured = capsys.readouterr()
        assert captured.out == output

    except:
        raise


def test_read_float1(monkeypatch, capsys):
    random_number = random.randint(50, 199) / 10
    inputs = iter([random_number])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    energy = efuel.read_float('')
    assert energy == random_number


def test_read_float2(monkeypatch, capsys):
    try:
        random_number = random.randint(150, 599) / 20
        inputs = iter([-4.2, 'a7', random_number])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        energy = efuel.read_float('')
        assert energy == random_number
    except ValueError:
        pytest.fail(
            'Formal falsche Werte werden nicht abgefangen. Dieser Test funktioniert nur für die erweiterte Version')


def test_read_float3(monkeypatch, capsys):
    try:
        random_number = random.randint(150, 599) / 25
        inputs = iter([-4.2, 'a7', random_number])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        efuel.read_float('')
        captured = capsys.readouterr()
        assert captured.out == 'Geben Sie eine positive Zahl ein\nGeben Sie eine positive Zahl ein\n'
    except ValueError:
        pytest.fail(
            'Formal falsche Werte werden nicht abgefangen. Dieser Test funktioniert nur für die erweiterte Version')


def test_read_timestamp1(monkeypatch, capsys):
    inputs = iter(['05.01.2023 13:37'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    timestamp = efuel.read_timestamp('')
    if isinstance(timestamp, str):
        assert timestamp == '05.01.2023 13:37'
    else:
        assert timestamp == datetime.strptime('05.01.2023 13:37', '%d.%m.%Y %H:%M')


def test_read_timestamp2(monkeypatch, capsys):
    try:
        inputs = iter(['05.01.2023 1a:05', '06.01.2023 13:10'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        timestamp = efuel.read_timestamp('')
        assert timestamp == datetime.strptime('06.01.2023 13:10', '%d.%m.%Y %H:%M')
    except ValueError:
        pytest.fail(
            'Formal falsche Werte werden nicht abgefangen. Dieser Test funktioniert nur für die erweiterte Version')


def test_read_timestamp3(monkeypatch, capsys):
    try:
        inputs = iter(['05.01.2023 1a:05', '06.01.2023 13:10'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        efuel.read_timesstamp('')
        captured = capsys.readouterr()
        assert captured.out == 'Geben Sie ein gültiges Datum/Uhrzeit ein\n'
    except ValueError:
        pytest.fail(
            'Formal falsche Werte werden nicht abgefangen. Dieser Test funktioniert nur für die erweiterte Version')


@pytest.fixture
def collection():
    accounts = efuel.init_accounts()
    if accounts is None:
        return 'UNBEKANNT'
    elif isinstance(accounts, list):
        return 'BASIS'
    elif isinstance(accounts, dict):
        return 'ERWEITERT'
    else:
        return 'UNBEKANNT'


@pytest.fixture
def attributes():
    fields = dataclasses.fields(Entry)
    datatype = fields[0].type
    if datatype is str:
        return 'BASIS'
    elif datatype is datetime:
        return 'ERWEITERT'
    else:
        return 'UNBEKANNT'


@pytest.fixture
def test_values():
    try:
        with open('./testdata.json') as json_file:
            data = json.load(json_file)
            data['energy_price'] = float(data['energy_price'])
            return data
    except FileNotFoundError:
        return 'Die Datei "testdata.json" fehlt. Kontaktieren Sie Ihre Lehrperson'
