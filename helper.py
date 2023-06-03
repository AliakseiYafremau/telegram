import sqlite3

def str_to_list(string):
    return string.split(', ')


def str_with_comma(string):
    return string.replace(' ', ', ')


def add_number(old, number):
    if len(old) == 0:
        return number
    else:
        return old + ' ' + number


def quit_number(old, number):
    if number in old:
        if ' ' not in old:
            return ''
        else:
            i = old.index(number)
            return old[:i - 1] + old[i + len(number):]
    return -1

def average(string):
    if string == '':
        return False
    lst = string.split(' ')
    n = [float(x) for x in lst]
    av = sum(n) / len(n)
    return av


def info(column, table_name):
    try:
        database = sqlite3.connect('database.db')
        cursor = database.cursor()
        cursor.execute("SELECT {0} FROM {1}".format(column, table_name))
        tpl = cursor.fetchall()
    finally:
        database.close()
    return tpl

def found(name, user):
    tpl = info('*', 'user_{0}'.format(user))
    index = [x[0] for x in tpl].index(name)
    return tpl, index


if __name__ == '__main__':
    print(average(''))
