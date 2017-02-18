#! /usr/bin/env python3


# Modules must contain:
#   definitions()
#   ui_definitions()
#   view_definitions()


app_name = "susm"

STATUS = {
    0: 'Dead',
    1: 'Egg',
    2: 'Infertile egg',
    3: 'Fertile egg',
    4: 'Damaged egg',
    5: 'Died off egg',
    6: 'Dead in shell',
    10: 'Pinkie',
    20: 'Fledgling',
    30: 'Weaned',
    40: 'Moulting',
}
"""
    1 (EGG) > 2 (INFERTILE EGG) > 0 (DEAD)
            > 3 (FETILE EGG) > 4 (DAMAGED EGG)  > 0 (DEAD)
                             > 5 (DIED OFF EGG) > 0 (DEAD)
                             > 6 (DIS)          > 0 (DEAD)
                             > 10 (PINKIE) > 0 (DEAD)
                                           > 20 (FLEDGLING) > 0 (DEAD)
                                                            > 30 (WEANED) > 0 (DEAD)
                                                                          > 40 (MOULTING) > 0 (DEAD)
                                                                                          > 100 (ADULT PLUMAGE)

    Transistions:
        0 #
        1 > 0,2,3,4
        2 > 0,4
        3 > 0,4,5,6,10
        4 > 0
        5 > 0
        6 > 0
    To:
        0 < *
        1 (+ = new)
        2 < 1
        3 < 1
        4 < 1,2,3
        5 < 2
        6 < 2
        10 < 2

    --- < 50: not yet a budgie
    --- 50-100: a sick bird.
    --- 100-150: a normal budgie
    --- 150-200:
    --- 200-250:
"""


def requirements():
    return ["base"]

def definitions(db, scope):
    return {}

def ui_definitions(db, scope):
    return {}

def view_definitions():

    name = 'Breeding Management'
    flow_name = name.upper()
    ref_name = "".join(c.lower() if c.isalnum() else "" for c in name)

    # Data queries.
    queries = {}
    queries["%s.locations" % (ref_name)] = ("result = Location.select(lambda bl: bl.type == Location.BREEDING).order_by(desc(Location.parent), desc(Location.name))", {})
    queries["%s.adults_in_location" % (ref_name)] = ("result = Individual.select(lambda adults: location.id == %(location_id)s and status > 50).order_by(desc(Individual.sex))", {'location_id': None})
    queries["%s.young_in_location" % (ref_name)] = ("result = Individual.select(lambda adults: location.id == %(location_id)s and 0 < status < 50).order_by(desc(Individual.dob))", {'location_id': None})

    # Views
    """
    VIEW
      [TAB*]
        [SECTION*]
          [LINE*]
            (LABEL? FIELD? BUTTON?)+

    Tabs:
        # All identical tabs, depending on the data:
            name, tabs[query,title], sections
        # Specific tabs:
            name, tabs[sections]

    Sections:
        title, lines

    Lines:
        query
    """
    views = {}
    views[flow_name] = {
        "name": name,
        "tabs": {
            "query": "%s.locations" % (ref_name),
            "title": ".name"
        },
        "sections": {
            0: {
                "title": "Parents",
                "lines": {
                    "query": "%s.adults_in_location" % (ref_name),
                    "elements": {
                        0: {
                            'type': 'label',
                            'value': '.sex'
                        },
                        1: {
                            'type': 'button',
                            'value': '.code',
                            'outmessage': "INDIVIDUAL"
                        },
                        2: {
                            'type': 'button',
                            'value': "X",
                            'outmessage': "REMOVE"
                        },
                    },
                    1: {
                        "elements": {
                            0: {
                                'type': 'button',
                                'value': "+",
                                'outmessage': "FINDPARENT"
                            }
                        }
                    }
                }
            },
            1: {
                "title": "Eggs/Chicks",
                "lines": {
                    "query": "%s.young_in_location" % (ref_name),
                    "elements": {
                        0: {
                            'type': 'button',
                            'value': '.code'
                        },
                        1: {
                            'type': 'label',
                            'if': '.status == 1',
                            'value': 'Egg'
                        },
                        2: {
                            'type': 'label',
                            'if': '.status == 2',
                            'value': 'Inf.'
                        },
                        3: {
                            'type': 'label',
                            'if': '.status == 3',
                            'value': 'Fert.'
                        },
                        4: {
                            'type': 'label',
                            'if': '.status == 4',
                            'value': 'Dam.'
                        },
                        5: {
                            'type': 'label',
                            'if': '.status == 5',
                            'value': 'Bad'
                        },
                        6: {
                            'type': 'label',
                            'if': '.status == 6',
                            'value': 'DIS'
                        },
                        7: {
                            'type': 'label',
                            'if': '6 < .status < 10',
                            'value': 'Egg?'
                        },
                        8: {
                            'type': 'label',
                            'if': '10 <= .status < 20',
                            'value': 'Pinkie'
                        },
                        9: {
                            'type': 'label',
                            'if': '20 <= .status < 30',
                            'value': 'Fledgling'
                        },
                        10: {
                            'type': 'label',
                            'if': '30 <= .status',
                            'value': 'Young'
                        },
                        21: {
                            'type': 'button',
                            'value': 'X'
                        },
                        22: {
                            'type': 'button',
                            'if': '.status == 1',
                            'value': 'Inf'
                        },
                        23: {
                            'type': 'button',
                            'if': '.status == 1',
                            'value': 'Fer'
                        },
                        24: {
                            'type': 'button',
                            'if': '.status in [1,2,3]',
                            'value': 'Dam'
                        },
                        25: {
                            'type': 'button',
                            'if': '.status == 1',
                            'value': 'Die'
                        },
                        26: {
                            'type': 'button',
                            'if': '.status == 1',
                            'value': 'DIS'
                        },
                        27: {
                            'type': 'button',
                            'if': '.status == 1',
                            'value': 'H'
                        }
                    },
                    1: {
                        'elements': {
                            0:{
                                'type': 'button',
                                'value': "+"
                            }
                        }
                    }
                }
            }
        }
    }

    flow = {}

    return (queries, views, {flow_name: flow})


if __name__ == "__main__":

    # jQuery URL's:
    #   /data/<Class>/<primary key>
    #   /query/<query name>?param1=value&param2=value

    # How to call queries

    test_queries = {}

    def do_query(name, scope=None, **kwargs):
        if scope is None:
            scope = {}
        query_template, defaults = test_queries[name]
        params = defaults.copy()
        params.update(kwargs)
        query = query_template % params
        exec("result = %s" % (query), scope)
        return scope['result']

    print("")
    print("===================")
    print("HOW TO CALL QUERIES")
    print("===================")
    print("")

    test_queries = {'test': ('result = [i+%(offset)s for i in range(limit)]', {'offset': 1})}
    queryname = 'test'

    limit = 5
    print("%s with limit %s: %s" % (queryname, limit, do_query(queryname, scope=locals())))

    limit = 3
    print("%s with limit %s: %s" % (queryname, limit, do_query(queryname, scope=locals(), offset=10)))

    print("")
    print("========")
    print("BREEDING")
    print("========")
    print("")

    (queries, views, flow) = view_definitions()
    for name, (query_template, query_defaults) in queries.items():
        print("Query %s: %s with %s." % (name, query_template, query_defaults))

    print("")


    class L():

        def __init__(self, id):
            self.id = id

        @property
        def parent(self):
            return None

        @property
        def name(self):
            return "BC %s" % self.id


    class I():
        
        def __init__(self, id, code=None, sex=None, status=None, location=None):
            self.id = id
            self.code = code
            self.sex = sex
            if status is None:
                status = 0
            self.status = status
            self.location = L(1)


    test_queries = {
        'breedingmanagement.adults_in_location': ('result = [I(1,"GOc",1,100), I(2,"VAYF",2,100)]', {}),
        'breedingmanagement.young_in_location': ('result = [%s]' % (",".join('I(%s,"(GOVAYF)%s",None,%s)' % (i+3, i+62, i) for i in [i for i in range(7)] + [(i+1)*10 for i in range(4)])), {}),
        'breedingmanagement.locations': ('result = [L(i+1) for i in range(limit)]', {})
    }

    limit = 3
    width = 70
    for name, definition in views.items():
        print("View %s" % (name))
        title = definition.get('name', name)
        # VIEW HEAD
        print("\t" + "=" * width)
        print("\t%s" % (title))
        print("\t" + "=" * width)
        tabs = definition.get('tabs', {0: {'title': ''}})
        tab_titles = []
        if 'query' in tabs:
            tab_title = tabs.get('title', name)
            tab_objects = do_query(tabs['query'], scope=locals())
            if tab_title[0] == ".":
                tab_titles = [getattr(tab, tab_title[1:]) for tab in tab_objects]
        else: # Loop over all integer keys and get out the titles.
            tab_titles = [tabs[i]['title'] for i in tabs.sorted() if isinstance(i, int)]
        tab_header = "|".join(tab_titles)
        tab_line_header = "+".join("-" * len(title) for title in tab_titles)
        # TAB HEAD
        print("\t+%s+" % tab_line_header)
        print("\t|%s|" % tab_header)
        print("\t|%s+%s+" % (" " * len(tab_titles[0]), "-" * (width - 3 - len(tab_titles[0]))))
        # SECTION
        sections = tabs.get('sections', definition.get('sections', {0: {'title': ''}}))
        for s in sorted(sections.keys(), key=str):
            if not isinstance(s, int):
                continue
            section_title = sections[s].get('title', '')
            print("\t| +-%s%s+ |" % (section_title, "-" * (width - 7 - len(section_title))))
            # LINES
            lines = sections[s].get('lines', tabs.get('lines', definition.get('sections', {0: {'title': ''}})))
            line_objects = []
            if 'query' in lines:
                line_objects = do_query(lines['query'], scope=locals())
            for line_object in line_objects:
                line_elements = []
                if 'elements' in lines:
                    for e in lines['elements']:
                        show = True
                        if 'if' in lines['elements'][e]:
                            exec("show = %s" % (lines['elements'][e]['if'].replace(".", "line_object.")), locals())
                            if not show:
                                continue
                        value = lines['elements'][e].get('value', '#')
                        if value[0] == ".":
                            value = getattr(line_object, value[1:])
                        if lines['elements'][e].get('type', '') == 'button':
                            line_elements.append("[%s]" % (value))
                        else:
                            line_elements.append(str(value))
                if line_elements:
                    line = " ".join(line_elements)
                    print("\t| | %s%s | |" % (line, " " * (width -8 - len(line))))
            for l in sorted(lines.keys(), key=str):
                if isinstance(l, int):
                    for e in sorted(lines[l]['elements']):
                        line = lines[l]['elements'][e].get('value', str(l))
                        if lines[l]['elements'][e].get('type', '') == 'button':
                            line = "[%s]" % (line)
                        print("\t| | %s%s | |" % (line, " " * (width - 8 - len(str(line)))))
            print("\t| +%s+ |" % ("-" * (width - 6)))
        # TAB TAIL
        print("\t+%s+" % ("-" * (width - 2)))
        # VIEW TAIL
        print("\t" + "=" * width)

    print("")

    for context, subflow in flow.items():
        print("Flow %s" % (context))
        for item in subflow:
            print("\t%s" % (subflow))

    print("")
