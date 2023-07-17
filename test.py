from dataclasses import dataclass


@dataclass
class Foo:
    a: str


class Bar(Foo):
    pass

p = Bar("h")

match p:
    case Foo(value):
        print("Inne")
    case other:
        print("Ikke")
