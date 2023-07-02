def test_execute_many(hnhm, cursor):
    hnhm.sql.execute("CREATE TABLE test(id int)")
    hnhm.sql.execute_many("INSERT INTO test(id) VALUES (%s)", [(1,), (2,), (3,)])

    cursor.execute("SELECT * FROM test")
    values = cursor.fetchall()
    assert len(values) == 3
