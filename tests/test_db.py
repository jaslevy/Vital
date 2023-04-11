import sys
import random
import psycopg2
from psycopg2 import pool
import time
import decimal

# Given a location id and its new quantities, update the SQL table

# make this into two separate functions for menstrual products and condoms


def update_quantities(location_id, new_tampon_quantity, new_pad_quantity, new_condom_quantity):
    assert location_id.isdigit(), 'non-integer location id'
    assert new_tampon_quantity == "None" or type(
        new_tampon_quantity) == int, 'non-integer tampon quantity'
    assert new_pad_quantity == "None" or type(
        new_pad_quantity) == int, 'non-integer pad quantity'
    assert new_condom_quantity == "None" or type(
        new_condom_quantity) == int, 'non-integer condom quantity'
    try:
        # This is the external database URL for our ElephantSQL instance
        postgreSQL_pool = pool.SimpleConnectionPool(1, 20, database='nbrexzdy', user='nbrexzdy',
                                                    password='SAOZ2b5HpPXqNx4Uc8cZkNpPQ_L1l0BR', host='peanut.db.elephantsql.com', port='5432')

        with postgreSQL_pool.getconn() as connection:
            with connection.cursor() as cursor:
                query = 'UPDATE quantities_test '
                query += 'SET '
                if new_tampon_quantity != "None":
                    query += f'tampon_count = {new_tampon_quantity}, '
                if new_pad_quantity != "None":
                    query += f'pad_count = {new_pad_quantity}, '
                if new_condom_quantity != "None":
                    query += f'condom_count = {new_condom_quantity}, '
                query += 'time_updated = NOW() '
                query += f'WHERE location_id = {location_id}'
                cursor.execute(query)
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

# ----------------------------------------------------------------------
# ----------------------------------------------------------------------


def get_data(menstrual_products, condoms):
    try:
        postgreSQL_pool = pool.SimpleConnectionPool(1, 20, database='nbrexzdy', user='nbrexzdy',
                                                    password='SAOZ2b5HpPXqNx4Uc8cZkNpPQ_L1l0BR', host='peanut.db.elephantsql.com', port='5432')

        with postgreSQL_pool.getconn() as connection:
            with connection.cursor() as cursor:
                query = 'SELECT l.location_id, '
                query += 'l.type_store, '
                query += 'l.building building, '
                query += 'l.room room, '
                query += 'l.floor_number floor, '
                query += 'l.longitude longitude, '
                query += 'l.latitude latiutude, '
                query += 'q.tampon_count tampon_count, q.pad_count pad_count, q.condom_count condom_count, '
                query += 'l.notes notes, '
                query += 'q.time_updated::DATE last_time_updated, '
                query += 'q.time_restocked::DATE last_time_restocked '
                query += 'FROM locations_test l '
                query += 'INNER JOIN quantities_test q '
                query += 'ON l.location_id = q.location_id '
                if menstrual_products and condoms:
                    query += f'WHERE l.type_store IN (\'menstrual products\',\'condoms\')'
                elif menstrual_products:
                    query += f'WHERE l.type_store=\'menstrual products\''
                elif condoms:
                    query += f'WHERE l.type_store=\'condoms\' '
                query += f'ORDER BY location_id'
                cursor.execute(query)
                return get_results(cursor)

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

# ----------------------------------------------------------------------
# ----------------------------------------------------------------------

# Return a list, where each entry is a class
# Input: cursor which contains executed query
# Output: results in list form


def get_results(cursor):
    row = cursor.fetchone()
    rows = []
    while row is not None:
        rows.append(row)
        row = cursor.fetchone()
    return rows

# ----------------------------------------------------------------------
# ----------------------------------------------------------------------


def get_buildings(menstrual, condom, aed):
    assert (menstrual in (0, 1) and condom in (0, 1) and aed in (0, 1)
            ), "Inputs are not in a valid format. Expects three (0, 1) integers"

    try:
        postgreSQL_pool = pool.SimpleConnectionPool(1, 20, database='nbrexzdy', user='nbrexzdy',
                                                    password='SAOZ2b5HpPXqNx4Uc8cZkNpPQ_L1l0BR', host='peanut.db.elephantsql.com', port='5432')

        with postgreSQL_pool.getconn() as connection:
            # 0 = 1 addition makes it so you never have bad sql query
            with connection.cursor() as cursor:
                query = 'SELECT building_id, building_name, \
                    latitude, longitude, has_menstrual, has_condom, \
                    has_aed, notes FROM buildings_test WHERE 0=1 '
                if menstrual:
                    query += 'OR has_menstrual = 1 '
                if condom:
                    query += 'OR has_condom = 1 '
                if aed:
                    query += 'OR has_aed = 1 '
                cursor.execute(query)
                results = get_results(cursor)
                if (menstrual or condom or aed):
                    assert len(results) > 0, "expected results but got none"
                if not (menstrual or condom or aed):
                    assert len(
                        results) == 0, "expected no results but got some"
                return results

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

# ----------------------------------------------------------------------
# ----------------------------------------------------------------------


def get_building_dict(menstrual, condom, aed):
    assert (menstrual in (0, 1) and condom in (0, 1) and aed in (0, 1)
            ), "Inputs are not in a valid format. Expects three (0, 1) integers"

    try:
        building_data = get_buildings(menstrual, condom, aed)
        quantity_data = get_data(menstrual, condom)
        if (menstrual or condom):
            assert (len(quantity_data) >
                    0), "expected location and quantity data but got none"

        result = {}

        for building in building_data:
            assert_building(building)
            result[building[1]] = {
                "building_info": {"latitude": building[2], "longitude": building[3], "has_menstrual": building[4], "has_condom": building[5], "has_aed": building[6], "notes": building[7]},
                "location_info": get_location_info(building[1], quantity_data)
            }
        return result

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

# ----------------------------------------------------------------------
# ----------------------------------------------------------------------


def assert_building(b):
    assert type(b[0]) == int, 'non-integer building id'
    assert (isinstance(b[1], str)), "building name should be a string"
    assert (isinstance(b[2], decimal.Decimal)
            and isinstance(b[3], decimal.Decimal)), "non-decimal latitude and longitudes"
    assert (b[4] in (0, 1) and b[5] in (0, 1) and b[6] in (
        0, 1)), "has_menstrual, has_pad, and has_condom should all be integers in (0, 1)"
    # print(b[7], type(b[7]))
    assert (isinstance(b[7], str) or b[7] is None), "notes should be a string"

# ----------------------------------------------------------------------
# ----------------------------------------------------------------------


def get_location_info(building_name, quantity_data):
    result = []
    for row in quantity_data:
        assert_location(row)
        if row[2] == building_name:
            result.append({"location_id": row[0], "room": row[3], "floor": row[4], "tampon_count": row[7], "pad_count": row[8],
                          "condom_count": row[9], "responsible_person": get_responsible_person(building_name), "notes": row[10]})
    return result

# ----------------------------------------------------------------------
# ----------------------------------------------------------------------


def assert_location(l):
    assert (type(l[0]) == int), 'non-integer location id'
    assert (l[1] in ("menstrual products", "condoms")
            ), 'type_store should be a string equaling either \'menstrual products\' or \'condoms\''
    assert (isinstance(l[2], str)
            ), "building name for location should be a string"
    assert (isinstance(l[3], str)), "room should be a string"
    assert (isinstance(l[4], str)), "floor should be a string"
    assert (type(l[7]) == int or l[7]
            is None), "tampon_count should be an integer"
    assert (type(l[8]) == int or l[8]
            is None), "pad_count should be an integer"
    assert (type(l[9]) == int or l[9]
            is None), "condom_count should be an integer"
    assert (isinstance(l[10], str)), "notes should be a string"

# ----------------------------------------------------------------------
# ----------------------------------------------------------------------


def get_responsible_person(building_name):
    # Mathey
    if building_name in ("Hamilton Hall", "Joline Hall", "Blair Hall, Little Hall", "Edwards Hall"):
        return "ang.jordan@princeton.edu"
    # Rocky -- change later once Rocky has a new res life coordinator
    elif building_name in ("Witherspoon Hall", "Holder Hall"):
        return "service@princeton.edu"
    # Butler
    elif building_name in ("Bloomberg Hall", "Yoselhoff Hall", "1967 Hall", "1976 Hall", "Wilf Hall", "Scully Hall"):
        return "caric.appleton@princeton.edu"
    # Whitman
    elif building_name in ("Fisher Hall", "Wendell Hall", "Lauritzen Hall", "Baker Hall", "1981 Hall"):
        return "gracelyn.yeboah@princeton.edu"
    # Forbes
    elif building_name in ("Forbes: New Wing", "Forbes: Main Building", "Items in Forbes: Annex"):
        return "alize.roberson@princeton.edu"
    # New College West
    elif building_name in ("Addy Hall", "Aliya Kanji Hall", "Kwanza M. Jones Hall", "José E. Feliciano Hall"):
        return "nia.pierce@princeton.edu"
    # Yeh
    elif building_name in ("Hariri Hall", "Fu Hall", "Grousbeck Hall", "Mannion Hall"):
        return "gian.ponticello@princetone.edu"
    else:
        return "service@princeton.edu"



def test_update_quantities(iters = 1, mp = 1, cond = 1):
    print("Testing update_quantities...")
    for _ in range(iters):
        print(_)
        old_location_data = get_data(mp, cond)  # database.get_data(mp, cond)
        num_locations = len(old_location_data)
        new_quants = [[random.randint(0, 4), random.randint(
            0, 4), random.randint(0, 4)] for _ in range(num_locations)]
        for j in range(min(10, len(old_location_data))):
            old_row = old_location_data[j]
            if old_row[7] is None:
                new_quants[j][0] = "None"
            if old_row[8] is None:
                new_quants[j][1] = "None"
            if old_row[9] is None:
                new_quants[j][2] = "None"

            update_quantities(
                f'{old_location_data[j][0]}', new_quants[j][0], new_quants[j][1], new_quants[j][2])
            # database.update_quantities(
            #     f'{old_location_data[j][0]}', new_quants[j][0], new_quants[j][1], new_quants[j][2])
        new_location_data = get_data(mp, cond)  # database.get_data(mp, cond)

        for j in range(10):

            if new_quants[j][0] != "None":
                assert (new_location_data[j][7] == new_quants[j][0])
            else:
                print("TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST ",
                      new_location_data[j][7])
                assert new_location_data[j][7] is None
            
            if new_quants[j][1] != "None":
                assert (new_location_data[j][8] == new_quants[j][1])
            else:
                assert new_location_data[j][8] is None

            if new_quants[j][2] != "None":
                assert (new_location_data[j][9] == new_quants[j][2])
            else:
                assert new_location_data[j][9] is None
    print("SUCCESS")

def test_get_buildings(mp, cond, aed):
    print("Testing get_building_dict...")
    building_dict = get_building_dict(mp, cond, aed)#database.get_building_dict(mp, cond, aed)
    location_count = get_location_count(building_dict)
    assert (location_count == len(get_data(mp, cond)))#len(database.get_data(mp, cond)))
    print("SUCCESS")

def get_location_count(building_dict):
    count = 0
    for key in building_dict:
        count += len(building_dict[key]["location_info"])
    return count 




def main():
    test_update_quantities(10, 1, 1)
    time.sleep(5)
    test_update_quantities(1, 0, 1)
    time.sleep(5)
    test_update_quantities(1, 1, 0)
    time.sleep(5)
    test_get_buildings(1, 1, 1)



if __name__ == "__main__": main()
