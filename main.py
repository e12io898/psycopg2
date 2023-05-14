import psycopg2

help = '''
    Программа для управления базой данных клиентами.
    Команды:
    ad - добавить нового клиента;
    ap - добавить телефон существующему клиенту;
    сс - изменить данные о клиенте;
    dp - удалить телефон из базы данных;
    dc - удалить клиента из базы данных;
    fc - найти клиента по имени, фамилии, email или телефону;
    ds - показать всю базу данных клиентов;
    h  - показать список команд;
    q  - выход из программы.

'''

# Создание базы данных
def create_db(conn):
    with conn.cursor() as cur:
        cur.execute('''
        CREATE TABLE IF NOT EXISTS client(
            client_id SERIAL PRIMARY KEY,
            first_name VARCHAR(30) NOT NULL,
            last_name VARCHAR(30) NOT NULL,
            email VARCHAR(50) NOT NULL UNIQUE
            );''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS client_phone(
            id SERIAL PRIMARY KEY,
            client_id INT REFERENCES client(client_id),
            phone BIGINT UNIQUE
            );''')


# Добавление нового клиента
def add_client(conn):
    print('''Введите данные нового клиента.
             Имя, фамилия и email - обязательные данные.
             Если телефона нет, пропустите данный запрос.
             --------------------------------------------''')

    first_name = input('Введите имя: ')
    last_name = input('Введите фамилию: ')
    email = input('Введите email: ')
    phone = input('Введите номер телефона: ')
    with conn.cursor() as cur:
        cur.execute(f'''
        INSERT INTO client(first_name, last_name, email)
        VALUES ('{first_name}', '{last_name}', '{email}')
        RETURNING client_id;''')

        client_id = cur.fetchone()[0]

    if phone != '':
        with conn.cursor() as cur:
            cur.execute(f'''
            INSERT INTO client_phone(client_id, phone)
            VALUES ({client_id}, {phone})
            ;''')


# Вывод информации о всех клиентах
def db_show(conn):
    with conn.cursor() as cur:
        cur.execute('''
        SELECT c.client_id, last_name, first_name, email, phone
        FROM client c
        JOIN client_phone cp ON c.client_id = cp.client_id
        ORDER BY last_name
        ;''')
        print(* cur.fetchall(), sep='\n')


# Выбор id-а клиента
def choice_id():
    print('Выберите id клиента из таблицы.')
    _ = input('Для вывода таблицы нажмите клавишу Enter.')
    db_show(conn)


# Добавить номер телефона клиенту
def add_phone(conn):
    choice_id()
    client_id = input('Введите id клиента: ')
    phone = input('Введите номер телефона: ')
    with conn.cursor() as cur:
        cur.execute(f'''
        INSERT INTO client_phone(client_id, phone)
        VALUES ({int(client_id)}, {int(phone)})
        ;''')

    print(f'Для клиента id-{client_id} добавлен номер {phone}.')


# Изменить данные о клиенте
def change_client(conn):
    choice_id()
    client_id = input('Введите id клиента: ')
    new_data = input('Введите новые данные клиента через пробел: )').split()
    first_name = new_data[0]
    last_name = new_data[1]
    email = new_data[2]
    phone = int(new_data[3])
    with conn.cursor() as cur:
        cur.execute('''
        UPDATE client
        SET first_name=%s, last_name=%s, email=%s
        WHERE client_id=%s
        ;''', (first_name, last_name, email, client_id,))

    with conn.cursor() as cur:
        cur.execute('''
        UPDATE client_phone
        SET phone=%s
        WHERE client_id=%s
        ;''', (phone, client_id,))

    print(f'Данные для клиента id-{client_id} обновлены.')


# Удалить телефон
def delete_phone(conn):
    choice_id()
    phone = input('Введите телефон, который хотите удалить: ')
    with conn.cursor() as cur:
        cur.execute('''
        DELETE FROM client_phone
        WHERE phone=%s
        ;''', (phone,))

    print(f'Телефон {phone} удалён из базы данных.')


# Удаление клиента из базы данных
def delete_client(conn):
    choice_id()
    client_id = input('Введите id клиента: ')
    with conn.cursor() as cur:
        cur.execute('''
        SELECT first_name, last_name
        FROM client
        WHERE client_id=%s
        ;''', (client_id,))

        info = cur.fetchone()

    with conn.cursor() as cur:
        cur.execute('''
        DELETE FROM client_phone
        WHERE client_id=%s
        ;''', (client_id,))

        cur.execute('''
        DELETE FROM client
        WHERE client_id=%s
        ;''', (client_id,))

    print(f'Клиент {info[0]} {info[1]} удалён из базы данных.')


# Поиск клиента
def find_client(conn):
    data = input('Введите имя, фамилию, email или телефон: ')
    if data.isalpha():
        with conn.cursor() as cur:
            cur.execute('''
            SELECT c.client_id, first_name, last_name, email, phone
            FROM client c
            JOIN client_phone cp ON c.client_id = cp.client_id
            WHERE first_name=%s
            OR last_name=%s
            OR email=%s
            ;''', (data, data, data))
            print(*cur.fetchall(), sep='\n')
    else:
        with conn.cursor() as cur:
            cur.execute('''
            SELECT c.client_id, first_name, last_name, email, phone
            FROM client c
            JOIN client_phone cp ON c.client_id = cp.client_id
            WHERE phone=%s
            ;''', (data,))
            print(*cur.fetchall(), sep='\n')

# Словарь с функциями.
func = {
    'ad': add_client,
    'ap': add_phone,
    'cc': change_client,
    'dp': delete_phone,
    'dc': delete_client,
    'fc': find_client,
    'ds': db_show
}

if __name__ == '__main__':
    print(help)
    command = input('Введите команду: ')
    with psycopg2.connect(database="clients_db", user="postgres",
                          password='123456') as conn:
        create_db(conn)
        while command != 'q':
            if command == 'h':
                print(help)
                command = input('Введите новую команду: ')
            else:
                func[command](conn)
                command = input('Введите новую команду: ')

    conn.close()


