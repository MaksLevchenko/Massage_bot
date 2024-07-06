class Master():
    id: int
    name: str
    foto: str
    title: str
    rating: float
    massages_ids: list

class Client():
    id: int
    name: str
    phone: str
    comment: str
    course: list[int]

class Massage():
    id: int
    name: str
    description: str
    price: int
    foto: str
