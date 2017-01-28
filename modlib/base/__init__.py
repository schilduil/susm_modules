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
    UI ORM definitions.
    """

    # So the other moduels are present.
    globals().update(scope)

    class UiIndividual(suapp.orm.UiOrmObject):
        """
        Individual for the UI that links to the back.
        """

        def __init__(self, id=None, code=None, orm=None, config=None):
            """
            Initializes the object by looking up or creating the database row.
            """
            if config:
                self._ui_config = config
            else:
                self._ui_config = suapp.orm.UiOrmObject.config
            if orm:
                # We're passing the orm object, ignoring the rest.
                self._ui_orm = orm
            elif id:
                self._ui_orm = modlib.base.Individual[id]
            elif code:
                self._ui_orm = pony.orm.get(i for i in modlib.base.Individual if i.code == code)
            # EMPTY ONE: DON'T CREATE?
            if self._ui_orm is None:
                print("Not found %s, %s, %s" % (id, code, orm))
            self.ui_init()

    UiIndividual.__module__ = 'modlib.base'

    return {'UiIndividual': UiIndividual}


if __name__ == "__main__":

    import os
    import sys
    import types

    print(os.getcwd())
    print(sys.path)
    sys.path.append(os.getcwd())

    import suapp.orm

    db = pony.orm.Database()

    modules = {'modlib': types.ModuleType('modlib', 'The modlib module'), 'modlib.base': types.ModuleType('modlib.base', 'Base')}
    globals().update(modules)
    sys.modules.update(modules)
    setattr(modlib, 'base', modules['modlib.base'])

    for name, obj in definitions(db, globals()).items():
        setattr(modules[obj.__module__], name, obj)

    for name, obj in ui_definitions(db, globals()).items():
        setattr(modules[obj.__module__], name, obj)

    db.bind("sqlite", ":memory:")
    db.generate_mapping(create_tables=True)

    with pony.orm.db_session():
        i = modlib.base.Individual(code="A")
        j = modlib.base.Individual(code="B")
        print("i: %s" % (i))
        print("j: %s" % (j))
        I = modlib.base.UiIndividual(orm=i)
        print(I)
        print("Flushing...")
        flush()
        J = modlib.base.UiIndividual(code="B")
        I2 = modlib.base.UiIndividual(code="A")
        print("J: %s" % (J))
        print("\t%s" % (J._ui_orm))
        print("\t%s" % (J.id))
        print("\t%s" % (J.code))
        print("I(2): %s" % (I2))
        print("\t%s" % (I2._ui_orm))
        print("\t%s" % (I2.id))
        print("\t%s" % (I2.code))
