from pony.orm import *


app_name = 'susm'


def requirements():
    """
    This is base, no requirements.
    """
    return []


def definitions(db, scope):
    """
    Entity definitions.
    """

    # Entity definition.
    class Individual(db.Entity):
        id = PrimaryKey(int, auto=True)
        code = Required(unicode, unique=True)
        sex = Optional(int, size=8, unsigned=True)
        status = Optional(int, size=8, unsigned=True)
        parents = Set('Individual', reverse='offspring')
        offspring = Set('Individual', reverse='parents')

    # Re-setting the module to leave out 'datamodel'.
    Individual.__module__ = 'modlib.base'

    # Returning the definitions.
    return {'Individual': Individual}


def ui_definitions(db, scope):
    """
    UI ORM definitions - TODO
    """
    return {}


if __name__ == "__main__":

    db = pony.orm.Database()

    definitions(db, globals())

    class ClosedRing(db.Entity):
        wearers = Set('Individual', reverse='closed_ring')
        issuer = Required(unicode, 3)
        breeder = Required(unicode)
        year = Required(int)
        size = Required(unicode, 2)
        sequence_number = Required(int)
        PrimaryKey(issuer, breeder, year, size, sequence_number)

    Individual.closed_ring = Optional(ClosedRing, reverse='wearers')

    db.bind("sqlite", ":memory:")
    db.generate_mapping(create_tables=True)

    print(dir(Individual))
    print(dir(ClosedRing))
