import psycopg2
data_base = {
    1: ('Иван', 'Иванов', 'ivanivanov@ya.ru', 89277788612),
    2: ('Сергей', 'Сергеев', 'sergserg@ya.ru', 889568546642),
    3: ('Александр', 'Иванов', 'alivanov@ya.ru', 88998798465),
    4: ('Юрий', 'Иванов', 'yuivanov@ya.ru', 86449484654, 8964568745),
    5: ('Иван', 'Сергеев', 'vanov@ya.ru', 89275556512, 8564965215),
    6: ('Анастасия', 'Красивая', 'krasanastas@mail.ru'),
    7: ('Юлия', 'Орешкина', 'yu@mail.ru'),
    8: ('Oleg', 'Oleg', 'oleg@mail.ru', 556487),
    9: ('Сергей', 'Викторович', '123456@rambler.ru', 963145678, 85612364785),
    10: ('Дарья', 'Алексеева', 'daraleck@mail.ru')
}

with psycopg2.connect(database="clients_db", user="postgres",
                      password='123456') as conn:
    for i in range(1, 11):
        with conn.cursor() as cur:
            cur.execute(f'''
            INSERT INTO client(first_name, last_name, email)
            VALUES {data_base[i][0:3]}
            RETURNING client_id;''')

            client_id = cur.fetchone()[0]
            print(client_id)

        if len(data_base[i]) == 4:
            with conn.cursor() as cur:
                cur.execute(f'''
                INSERT INTO client_phone(client_id, phone)
                VALUES ({client_id}, {data_base[i][3]})
                ;''')
        elif len(data_base[i]) > 4:
            for number in data_base[i][3:]:
                with conn.cursor() as cur:
                    cur.execute(f'''
                    INSERT INTO client_phone(client_id, phone)
                    VALUES ({client_id}, {number})
                    ;''')

conn.close()