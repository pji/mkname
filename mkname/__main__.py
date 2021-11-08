"""
__main__

The mainline for mkname.
"""
from mkname import db
from mkname.constants import LOCAL_CONFIG
from mkname.dice import roll
from mkname.mkname import build_compound_name, get_config, select_name
from mkname.mod import add_scifi_letters, garble


def main() -> None:
    config = get_config(LOCAL_CONFIG)
    names_info = db.get_names(config['db_path'])
    names = [name_info.name for name_info in names_info]
    name = build_compound_name(names)

    if roll('1d6') == 1:
        name = add_scifi_letters(name)
    if roll('1d6') == 1:
        name = garble(name)

    print(name)
    print()

main()