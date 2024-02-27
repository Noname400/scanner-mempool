from prettytable import PrettyTable
from function import *

def sel_db_research():
    q, conn = check_database(DB["ip"], DB["db"], DB["user"], DB["password"])
    if q:
        cur = conn.cursor()
        cur.execute("SELECT * FROM public.research ORDER BY counter DESC, date_update DESC LIMIT 100")
        data = cur.fetchall()
        cur.close()
        conn.close()
        if data:
            headers = [desc[0] for desc in cur.description]
            table = PrettyTable(headers)
            table.align["pair_name"] = "l"
            table.max_width["pair_name"] = 25
            table.max_width["dex_name"] = 35
            table.max_width["pair_price"] = 36

            for row in data:
                formatted_row = list(row)
                #########################################################
                pair_name_index = headers.index("pair_name")
                pair_name_value = formatted_row[pair_name_index]
                formatted_row[pair_name_index] = pair_name_value[:25]
                #########################################################
                pair_name_index = headers.index("pair_price")
                pair_name_value = formatted_row[pair_name_index]
                formatted_row[pair_name_index] = pair_name_value[:36]
                #########################################################
                pair_name_index = headers.index("dex_name")
                pair_name_value = formatted_row[pair_name_index]
                formatted_row[pair_name_index] = pair_name_value[:35]
                #########################################################
                formatted_row[headers.index("pair_price")] = "{:.2f}".format(row[headers.index("pair_price")])
                table.add_row(formatted_row)
            
            print(table)
        else:
            print("Нет данных для отображения")
    else:
        print("Не удалось подключиться к базе данных")

# Пример использования
sel_db_research()
