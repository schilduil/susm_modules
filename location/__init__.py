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
        (modlib.base.Individual, 'location', Optional('Location'))
    ]

    # TODO: we might want this code in some module.
    for (entity, name, attr) in new_columns:
        attr._init_(entity, name)
        entity._attrs_.append(attr)
        entity._new_attrs_.append(attr) 
        entity._adict_[name] = attr
        setattr(entity, name, attr)

    # New entity for location.
    class Location(db.Entity):
        id = PrimaryKey(int, auto=True)
        name = Required(unicode)
        parent = Optional('Location', reverse='childeren')
        childeren = Set('Location', reverse='parent', cascade_delete=True)
        individuals = Set(modlib.base.Individual)
        composite_key(parent, name)

    # Adjusting the module to remove 'datamodel'.
    Location.__module__ = 'modlib.location'

    # Returning the entities.
    return {'Location': Location}
