from datetime import date
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
        (modlib.base.Individual, 'second_kinships', Set('Kinship', reverse='second')),
        (modlib.base.Individual, 'dob', Optional(date))
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
        pc_kinship = Optional(float)
        PrimaryKey(first, second)

    # Adjusting the module to remove 'datamodel'.
    Kinship.__module__ = 'modlib.kinship'

    # Returning the entities.
    return {'Kinship': Kinship}


def ui_definitions(db, scope):
    """
    UI ORM definitions.
    """

    # So the other moduels are present.
    globals().update(scope)

    class UiKinship(suapp.orm.UiOrmObject):
        """
        Calculates and retrieves/saves kinships.
        """
        _ui_class = modlib.kinship.Kinship

        @staticmethod
        def _calculate(first, second):
            """
            Calculates the kinship based on the kinship of parents.
            """
            # Anything with an unknown is considered 0.0
            if first is None or second is None:
                return 0.0
            # If first isn't the oldest, switch.
            try:
                if first.dob > second.dob:
                    first, second = second, first
            except (TypeError, AttributeError):
                try:
                    if first.id > second.id:
                        first, second = second, first
                except (TypeError, AttributeError):
                    if first > second:
                        first, second = second, first
            # Get the parents of the youngest.
            parents = second.parents.page(1, pagesize=2)
            # If first == second, handle it.
            if first == second:
                # Kinship with itself:
                # kinship(a,a) = (1.0 + kinship(a.dad, a.mum)) / 2.0
                if len(parents) == 2:
                    result = (1.0 + UiKinship(first=parents[0], second=parents[1]).kinship) / 2.0
                else:
                    # At least one unknown parent, so assuming unibred.
                    result = (1.0 + 0.0) / 2.0
            else:
                # If they are different this is the formula:
                # kinship(a,b) = (kinship(b, a.dad) + kinship(b, a.mum)) / 2.0
                result = 0.0
                for parent in parents:
                    # Best bet is that the parent is older.
                    result += UiKinship(first=parent, second=first).kinship / 2.0
            return result

        @staticmethod
        def _calculate_pc(first, second):
            """
            Calculates the kinship based on the kinship of parents.
            """
            # Anything with an unknown is considered 0.0
            if first is None or second is None:
                return 0.0
            # If first isn't the oldest, switch.
            try:
                if first.dob > second.dob:
                    first, second = second, first
            except (TypeError, AttributeError):
                try:
                    if first.id > second.id:
                        first, second = second, first
                except (TypeError, AttributeError):
                    if first > second:
                        first, second = second, first
            # Get the parents of the youngest.
            parents = second.parents.page(1, pagesize=2)
            # If first == second, handle it.
            if first == second:
                # Kinship with itself:
                # pc_kinship(a,a) = (1.0) / 2.0
                result = (1.0 + 0.0) / 2.0
            else:
                # If they are different this is the formula:
                # pc_kinship(a,b) = (pc_kinship(b, a.dad) + pc_kinship(b, a.mum)) / 2.0
                result = 0.0
                for parent in parents:
                    # Best bet is that the parent is older.
                    pc = UiKinship(first=parent, second=first).pc_kinship / 2.0
                    if pc is None:
                        # Falling back to the kinship if we don't have a pc_kinship.
                        # After all pc_kinship is optional.
                        pc = UiKinship(first=parent, second=first).kinship / 2.0
                    result += pc
            return result

        def __init__(self, first=None, second=None, orm=None, config=None):
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
            else:
                # TODO: make a specific exception.
                if first is None or second is None:
                    raise KeyError("Either orm or first & second must be specified.")
                # The individuals should be the db orm object.
                if isinstance(first, suapp.orm.UiOrmObject):
                    first = first._ui_orm
                if isinstance(second, suapp.orm.UiOrmObject):
                    second = second._ui_orm
                # Normally first should be the oldest, otherwise it is switched.
                self._ui_switched = False
                try:
                    if first.dob > second.dob:
                        self._ui_switched = True
                except (TypeError, AttributeError):
                    try:
                        if first.id > second.id:
                            self._ui_switched = True
                    except (TypeError, AttributeError):
                        if first > second:
                            self._ui_switched = True
                # We don't need the objects but the id
                try:
                    id1, id2 = first.id, second.id
                except (TypeError, AttributeError):
                    # Assuming it was already the id's.
                    id1, id2 = first, second
                # Try to find it
                try:
                    # Normally it should be in the database with the oldest first.
                    if self._ui_switched:
                        self._ui_orm = modlib.kinship.Kinship[id2, id1]
                    else:
                        self._ui_orm = modlib.kinship.Kinship[id1, id2]
                except core.ObjectNotFound:
                    self._ui_switched = not self._ui_switched
                    try:
                        if self._ui_switched:
                            self._ui_orm = modlib.kinship.Kinship[id2, id1]
                        else:
                            self._ui_orm = modlib.kinship.Kinship[id1, id2]
                    except core.ObjectNotFound:
                        self._ui_switched = not self._ui_switched
                        # This will not work with just id's.
                        self.calculate_and_create(first, second)
            self.ui_init()

        def calculate_and_create(self, first, second):
            """
            Calculates the kinship and creates the database object.
            """
            kinship = self._calculate(first, second)
            pc_kinship = self._calculate_pc(first, second)
            if self._ui_switched:
                self._ui_orm = modlib.kinship.Kinship(first=second, second=first, kinship=kinship, pc_kinship=pc_kinship)
            else:
                self._ui_orm = modlib.kinship.Kinship(first=first, second=second, kinship=kinship, pc_kinship=pc_kinship)

        def recalculate(self, timestamp=None):
            """
            Recalculates the kinship.

            To be triggered from Individual if a parentage (or dob?) changes. Also
            updates all depended objects.
            It uses the time stamp to avoid redoing firsts that already were dfirst.
            """
            # Initializing the time stamp if needed.
            if not timestamp:
                timestamp = datetime.datetime.now()
            if self._ui_update_timestamp:
                if self._ui_update_timestamp >= timestamp:
                    # It was already updated after the time stamp: skipping.
                    return
            # Recalculating this.
            kinship = self._calculate(self._ui_orm.first, self._ui_orm.second)
            self._ui_orm.kinship = kinship
            # Marking the timestamp we did the update.
            self._ui_update_timestamp = datetime.datetime.now()
            # Find all the children's kinships and update them.
            for child in self._ui_orm.first.childeren:
                for kinship in child.kinships:
                    kinship.recalculate(timestamp=timestamp)
            for child in self._ui_orm.second.childeren:
                for kinship in child.kinships:
                    kinship.recalculate(timestamp=timestamp)

    # Adjusting the module to remove 'datamodel'.
    UiKinship.__module__ = 'modlib.kinship'

    class Kinship_UiIndividual(modlib.base.UiIndividual):
        METHOD_CLASSIC = 0
        METHOD_PC = 1

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.ui_attributes.add('ui_inbreeding')
            # HIDDEN: self.ui_attributes.add('_ui_pc_inbreeding')

        def ui_which_kinship(self):
            try:
                if self._ui_config['modules']['kinship']['method'].lower() == 'pc':
                    return Kinship_UiIndividual.METHOD_PC
            except KeyError:
                pass
            return Kinship_UiIndividual.METHOD_CLASSIC

        @property
        def ui_inbreeding(self):
            if self.ui_which_kinship == METHOD_PC:
                return self._ui_pc_inbreeding
            else:
                return self._ui_inbreeding

        @ui_inbreeding.setter
        def ui_inbreeding(self, f):
            self._ui_inbreeding = f

        @property
        def _ui_inbreeding(self):
            kinship = modlib.kinship.UiKinship(first=self._ui_orm, second=self._ui_orm)
            return (2.0 * kinship.kinship) - 1.0

        @_ui_inbreeding.setter
        def ui_inbreeding(self, f):
            # TODO: raise an exception if this can be calculated from the parents.
            kinship = modlib.kinship.UiKinship(first=self._ui_orm, second=self._ui_orm)
            kinship.kinship = (1.0 + f) / 2.0

        @property
        def _ui_pc_inbreeding(self):
            try:
                parents = self._ui_orm.parents.page(1, pagesize=2)
                return UiKinship(first=parents[0], second=parents[1]).pc_kinship
            except:
                # Fall back to the kinship.
                return self._ui_inbreeding()
            return pc_kinship

    # Adjusting the module.
    Kinship_UiIndividual.__module__ = 'modlib.base'

    # Returning the entities.
    return {'UiIndividual': Kinship_UiIndividual, 'UiKinship': UiKinship}

def view_definitions():
    return (None, None, None)
