#! /usr/bin/env python3


# Modules must contain:
#   definitions()
#   ui_definitions()
#   view_definitions()


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
                             
    --- < 50: not yet a budgie
    --- 50-100: a sick bird.
    --- 100-150: a normal budgie
    --- 150-200:
    --- 200-250:
"""

def view_definitions():

    name = 'Breeding Management'
    flow_name = name.upper()
    ref_name = "".join(c.lower() if c.isalnum() else "" for c in name)

    # Data queries.
    queries = {}
    queries["%s.locations" % (ref_name)] = ("result = Location.select(lambda bl: bl.type == Location.BREEDING).order_by(desc(Location.parent), desc(Location.name))", {})
    queries["%s.adults_in_location" % (ref_name)] = ("result = Individual.select(lambda adults: location.id == %(location_id)s and status > 50).order_by(desc(Individual.sex))", {'location_id': None})
    queries["%s.young_in_location" % (ref_name)] = ("result = Individual.select(lambda adults: location.id == %(location_id)s and 0 < status < 50).order_by(desc(Individual.dob))", {'location_id': None})
    # TODO: register queries.

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
                                'value': "Add",
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
                            'type': 'label',
                            'condition': '.status == 1',
                            'value': 'Egg'
                        },
                        1: {
                            'type': 'label',
                            'condition': '.status == 2',
                            'value': 'Inf.'
                        },
                        2: {
                            'type': 'label',
                            'condition': '.status == 3',
                            'value': 'Fert.'
                        },
                        3: {
                            'type': 'label',
                            'condition': '.status == 4',
                            'value': 'Dam.'
                        },
                        4: {
                            'type': 'label',
                            'condition': '.status == 5',
                            'value': 'Bad'
                        },
                        5: {
                            'type': 'label',
                            'condition': '.status == 6',
                            'value': 'DIS'
                        },
                    }
                }
            }
        }
    }
    # TODO: register with Jeeves.

    flow = {}
    # TODO: register in the flow under flow_name.

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
        'breedingmanagement.young_in_location': ('result = [I(3,"(GOVAYF)62",None,10), I(4,"(GOVAYF)67",None,1)]', {}),
        'breedingmanagement.locations': ('result = [L(i+1) for i in range(limit)]', {})
    }

    limit = 3
    width = 60
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
        # TAB HEAD
        print("\t+%s+" % ("-" * len(tab_header)))
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
                        value = lines['elements'][e].get('value', '#')
                        if value[0] == ".":
                            value = getattr(line_object, value[1:])
                        line_elements.append(str(value))
                line = " ".join(line_elements)
                print("\t| | %s%s | |" % (line, " " * (width -8 - len(line))))
            for l in sorted(lines.keys(), key=str):
                if isinstance(l, int):
                    print("\t| | %s%s | |" % (l, " " * (width - 8 - len(str(l)))))
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
