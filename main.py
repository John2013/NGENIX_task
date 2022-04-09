from random import randint
from uuid import uuid4

from faker import Faker
from jinja2 import Environment, PackageLoader, select_autoescape


FAKE = Faker('ru_RU')


def generate_objects(objects_count: int = 100):
    for object_number in range(objects_count):
        yield {
            "id": uuid4(),
            "level": randint(0, 100),
            "objects": [FAKE.company() for _ in range(randint(1, 10))],
            "number": object_number
        }


def save_objects():
    env = Environment(
        loader=PackageLoader("main"),
        autoescape=select_autoescape(enabled_extensions=('xml',))
    )
    template = env.get_template("objects.xml")
    for generated_object in generate_objects():
        template.stream(**generated_object).dump(
            f'results/object{generated_object["number"]}.xml')


if __name__ == '__main__':
    save_objects()
