import circular_import_b

class B:
    def bar(self):
        return circular_import_a.A()
