def main():
    accounting = init_accounts()
    add_entries(accounting)
    show_balance(accounting)


def init_accounts():
    return None


def add_entries():
    pass


def read_entry():
    return None


def show_balance():

    # Basisversion: Zeile mit Datum und Kosten
    # print(f'  - {DATUM}\tCHF {KOSTEN:.2f}')

    # Erweitert: Zeile mit Datum und Kosten
    # print(f'  - {DATUM:%d.%m.%Y %H:%M}\tCHF {KOSTEN:.2f}')

    # Beide Versionen: Zeile mit Total
    # print(f'{"Total:":<20}\tCHF {TOTAL:.2f}')

    pass


def read_float():
    return 13.79


def read_datetime():
    return '01.01.2099 00:01'


if __name__ == '__main__':
    main()
