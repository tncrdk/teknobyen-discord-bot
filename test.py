from typing import Protocol


class Foo(Protocol):
    def bar(self, *args):
        ...

class Baz:
    def bar(self, name, parameter):
        print(f"{name}, {parameter}")

def func(test: Foo, *args):
    test.bar(*args)

