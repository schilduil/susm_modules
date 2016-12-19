from pony.orm import *


app_name = "susm"


def requirements():
    """
    Other modules required for kinship: base.
    """
    return ['base']


def definitions(db, scope):

    # So the other modules are present.
    globals().update(scope)

    # New columns for entities in required modules.
    new_columns = [
        (modlib.base.Individual, 'first_kinships', Set('Kinship', reverse='first')),
        (modlib.base.Individual, 'second_kinships', Set('Kinship', reverse='second'))
    ]

    # TODO: we might want this code in some module.
    for (entity, name, attr) in new_columns:
        attr._init_(entity, name)
        entity._attrs_.append(attr)
        entity._new_attrs_.append(attr)
        entity._adict_[name] = attr
        setattr(entity, name, attr)

    # New entity for kinship.
    class Kinship(db.Entity):
        first = Required(modlib.base.Individual, reverse='first_kinships')
        second = Required(modlib.base.Individual, reverse='second_kinships')
        kinship = Required(float)
        PrimaryKey(first, second)

    # Adjusting the module to remove 'datamodel'.
    Kinship.__module__ = 'modlib.kinship'

    # Returning the entities.
    return {'Kinship': Kinship}
