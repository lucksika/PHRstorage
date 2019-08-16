from starbase.client.table import scanner
import starbase

HBASE_HOST = '10.0.0.1'
HBASE_PORT = 9000


def save_batch(table, rowkey, batch_data):
    c = starbase.Connection(port=HBASE_PORT)
    # c = starbase.Connection(host=HBASE_HOST, port=HBASE_PORT)
    table = c.table(table)

    b = table.batch()
    if b:
        b.insert(rowkey, batch_data)
        b.commit(finalize=True)


def fetch(table, rowkey, *args):
    c = starbase.Connection(port=HBASE_PORT)
    # c = starbase.Connection(host=HBASE_HOST, port=HBASE_PORT)
    table = c.table(table)
    if not args:
        return table.fetch(
            rowkey,
        )

    return table.fetch(
        rowkey, args
    )


def fetch_all(table):
    c = starbase.Connection(port=HBASE_PORT)
    # c = starbase.Connection(host=HBASE_HOST, port=HBASE_PORT)
    table = c.table(table)

    return table.fetch_all_rows(with_row_id=False, scanner_config='<Scanner maxVersions="1"></Scanner>')


def fetch_all_with_row_id(table):
    c = starbase.Connection(port=HBASE_PORT)
    # c = starbase.Connection(host=HBASE_HOST, port=HBASE_PORT)
    table = c.table(table)

    return table.fetch_all_rows(with_row_id=True, scanner_config='<Scanner maxVersions="1"></Scanner>')


def fetch_from(table, start_row, *args):
    c = starbase.Connection(port=HBASE_PORT)
    # c = starbase.Connection(host=HBASE_HOST, port=HBASE_PORT)
    print "fetch_from > start_row: ", start_row
    table = c.table(table)
    if not args:
        return table.fetch_all_rows(with_row_id=False, fail_silently=True, scanner_config='<Scanner maxVersions="1" startRow="{}"></Scanner>'.format(start_row))
    else:
        return table.fetch_all_rows(with_row_id=False, fail_silently=True, scanner_config='<Scanner maxVersions="1" startRow="{}" endRow="{}"></Scanner>'.format(start_row, args[0]))


def fetch_from_with_row_id(table, start_row, *args):
    c = starbase.Connection(port=HBASE_PORT)
    # c = starbase.Connection(host=HBASE_HOST, port=HBASE_PORT)
    print "fetch_from > start_row: ", start_row
    table = c.table(table)
    if not args:
        return table.fetch_all_rows(with_row_id=True, fail_silently=True, scanner_config='<Scanner maxVersions="1" startRow="{}"></Scanner>'.format(start_row))
    else:
        return table.fetch_all_rows(with_row_id=True, fail_silently=True, scanner_config='<Scanner maxVersions="1" startRow="{}" endRow="{}"></Scanner>'.format(start_row, args[0]))


def fetch_part(table, start_row, end_row, *args):
    c = starbase.Connection(port=HBASE_PORT)
    # c = starbase.Connection(host=HBASE_HOST, port=HBASE_PORT)
    table = c.table(table)
    if not args:
        return table.fetch_all_rows(with_row_id=True, fail_silently=True, scanner_config='<Scanner maxVersions="1" startRow="{}" endRow="{}"></Scanner>'.format(start_row, end_row))
    else:
        return table.fetch_all_rows(with_row_id=True, fail_silently=True, scanner_config='<Scanner maxVersions="1" startRow="{}" endRow="{}"><column>{}</column></Scanner>'.format(start_row, end_row, args[0]))


def insert_data(table, rowkey, columfamily, columqualifier, value):
    c = starbase.Connection(port=HBASE_PORT)
    # c = starbase.Connection(host=HBASE_HOST, port=HBASE_PORT)
    table = c.table(table)

    table.insert(
        rowkey,
        {
            columfamily: {
                columqualifier: value
            }
        }
    )


def delete_row(table, rowkey):
    c = starbase.Connection(port=HBASE_PORT)

    table = c.table(table)

    table.remove(rowkey)


def all_tables():
    c = starbase.Connection(port=HBASE_PORT)
    tables = c.tables()
    return tables


def create_table(table_name, table_column):
    c = starbase.Connection(port=HBASE_PORT)
    new_table = c.table(table_name)
    new_table.create(table_column)
    exists = new_table.exists()
    return exists

def all_columns(table):
    c = starbase.Connection(port=HBASE_PORT)
    t = c.table(table)
    columns = t.columns()
    return columns