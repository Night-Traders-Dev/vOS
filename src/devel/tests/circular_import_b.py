import circular_import_a

class B:
    def bar(self):
        return circular_import_a.A()
