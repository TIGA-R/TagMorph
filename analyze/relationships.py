from typing import Generator, Literal
type SqliteDatatype = Literal['INTEGER', 'REAL', 'TEXT', 'BLOB']

def build_child_parent(
        tags: dict[int, tuple[str, str, str, str]],
        names: dict[str, int]
    ) -> dict[int, int|None]:
    # udt_dict = {
    #     info[3].lstrip('_types_/')+'/'+info[0]: id 
    #     for id, info in tags.items()
    #     if info[1] in ('UdtInstance', 'UdtType')
    # } 
    # import pprint
    # pprint.pprint(udt_dict)
    
    return {id: names.get(info[2]) for id, info in tags.items() if info[2]}

def get_parents(id: int, child_parent_dict: dict[int, int|None]) -> list[int]:
    parent_list: list[int] = []
    def add_parent(id: int, child_parent_dict: dict[int, int|None]) -> None:
        nonlocal parent_list
        parent = child_parent_dict.get(id)
        if parent is None:
            return
        else:
            parent_list.append(parent)
            add_parent(parent, child_parent_dict)
    add_parent(id, child_parent_dict)
    return parent_list

def get_children(id: int, child_parent_dict: dict[int, int|None]) -> list[int]:
    return [key for key, val in child_parent_dict.items() if val == id]

def atom_tag_gen_build(
    atom_dict: dict[int, tuple[str, int]], 
    udt_inst_dict: dict[int, str], 
    child_parent_dict: dict[int, int|None], 
) -> Generator[str, None, None]:
    return (name + '/' + atom[0] 
        for id, name in udt_inst_dict.items()
        for parent in get_parents(id, child_parent_dict) 
        for atom in atom_dict.values() 
        if parent == atom[1]
    )

def build_test_database(
    file_path: str,
    table_name: str,
    data_generator: Generator[str, None, None],
    audit_columns: dict[str, SqliteDatatype]={'original': 'TEXT', 'modified': 'TEXT'},
) -> None: 
    import sqlite3
    with sqlite3.connect(file_path) as conn:
        c = conn.cursor()
        column_string = ''.join([f", {key} {value} NULL" for key, value in audit_columns.items()])
        c.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} (id int,  tagpath TEXT NOT NULL{column_string});""")
        for idx, line in enumerate(data_generator):
            sql = """insert into %s (id, tagpath) values(?, ?)"""%table_name
            # print(line)
            c.execute(sql, (idx, line,))
        conn.commit()

