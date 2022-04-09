import shutil
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
            f'xmls/object{generated_object["number"]}.xml')


def archive_objects(archive_number: int):
    shutil.make_archive(f'archives/objects_{archive_number}', 'zip', 'xmls')


def make_archives(archives_count: int = 50):
    for archive_number in range(archives_count):
        save_objects()
        archive_objects(archive_number)


if __name__ == '__main__':
    make_archives()
