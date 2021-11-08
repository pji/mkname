"""
__main__
~~~~~~~~

The mainline for mkname.
"""
from mkname import db
from mkname import mkname as mn
from mkname.dice import roll
from mkname.mod import add_scifi_letters, garble


def main() -> None:
    config = mn.get_config()
    db_loc = mn.init_db(config['db_path'])
    names_info = db.get_names(db_loc)
    names = [name_info.name for name_info in names_info]
    name = mn.build_compound_name(names)

    if roll('1d6') == 1:
        name = add_scifi_letters(name)
    if roll('1d6') == 1:
        name = garble(name)

    print(name)
    print()

main()