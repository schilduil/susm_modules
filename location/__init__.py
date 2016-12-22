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


def ui_definitions(db, scope):
    """
    UI ORM objects - TODO
    """

    # So the other moduels are present.
    globals().update(scope)

    class UiLocation(suapp.orm.UiOrmObject):
        """
        Individual for the UI that links to the back.
        """

        def __init__(self, parent=None, name=None, orm=None):
            """
            Initializes the object by looking up or creating the database row.
            """
            if orm:
                # We're passing the orm object, ignoring the rest.
                self._ui_orm = orm
            elif name and parent:
                self._ui_orm = modlib.location.Location[parent, name]
            # EMPTY ONE: DON'T CREATE?
            if self._ui_orm is None:
                print("Not found %s, %s, %s" % (id, code, orm))
            self.ui_init()

    UiLocation.__module__ = 'modlib.location'

    return {'UiLocation': UiLocation}
