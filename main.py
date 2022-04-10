import csv
import os
import shutil
import zipfile
from multiprocessing import Pool
from random import randint
from typing import Iterable
from uuid import uuid4
from xml.etree import ElementTree
from faker import Faker
from jinja2 import Environment, PackageLoader, select_autoescape


FAKE = Faker("ru_RU")
ARCHIVES_COUNT = 50
OBJECTS_COUNT = 100


def make_dirs(dirs: Iterable[str]):
    for directory in dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)


def generate_objects():
    for object_number in range(OBJECTS_COUNT):
        yield {
            "id": uuid4(),
            "level": randint(0, 100),
            "objects": [FAKE.company() for _ in range(randint(1, 10))],
            "number": object_number,
        }


def save_objects():
    env = Environment(
        loader=PackageLoader("main"),
        autoescape=select_autoescape(enabled_extensions=("xml",)),
    )
    template = env.get_template("objects.xml")
    for generated_object in generate_objects():
        template.stream(**generated_object).dump(
            os.path.join("xmls", f'object{generated_object["number"]}.xml')
        )


def zip_objects(archive_number: int):
    shutil.make_archive(
        os.path.join("archives", f"objects_{archive_number}"), "zip", "xmls"
    )


def make_archives():
    for archive_number in range(ARCHIVES_COUNT):
        save_objects()
        zip_objects(archive_number)


def unzip_objects(archive_number: int):
    unzip_path = os.path.join("xmls", f"archive_{archive_number}")
    with zipfile.ZipFile(
        os.path.join("archives", f"objects_{archive_number}.zip")
    ) as archive:
        archive.extractall(unzip_path)


def parse_object(archive_number: int, object_number: int) -> tuple[str, int, list[str]]:
    file_path = os.path.join(
        "xmls", f"archive_{archive_number}", f"object{object_number}.xml"
    )
    root_node = ElementTree.parse(file_path).getroot()
    object_id: str = root_node.find('./var[@name="id"]').attrib["value"]
    level = int(root_node.find('./var[@name="level"]').attrib["value"])
    objects: list[str] = []
    for object_tag in root_node.findall("objects/object"):
        objects.append(object_tag.attrib["name"])
    return object_id, level, objects


def collect_archive(archive_number: int):
    levels: list[tuple[str, int]] = []
    objects: list[tuple[str, list[str]]] = []
    unzip_objects(archive_number)
    for object_number in range(OBJECTS_COUNT):
        object_id, level, objects_list = parse_object(archive_number, object_number)
        levels.append((object_id, level))
        objects.append((object_id, objects_list))
    return levels, objects


def collect_objects_data() -> tuple[list[tuple[str, int]], list[tuple[str, list[str]]]]:
    levels: list[tuple[str, int]] = []
    objects: list[tuple[str, list[str]]] = []
    with Pool(os.cpu_count()) as pool:
        parts = pool.map(collect_archive, range(ARCHIVES_COUNT))
    for part_levels, part_objects in parts:
        levels.extend(part_levels)
        objects.extend(part_objects)
    return levels, objects


def save_csv(levels: list[tuple[str, int]], objects: list[tuple[str, list[str]]]):
    with open("levels.csv", "w", newline="") as csv_levels:
        writer = csv.writer(csv_levels)
        writer.writerow(("id", "level"))
        writer.writerows(levels)
    with open("objects.csv", "w", newline="", encoding="utf-8") as scv_objects:
        writer = csv.writer(scv_objects)
        writer.writerow(("id", "object"))
        for object_id, object_list in objects:
            for object_name in object_list:
                writer.writerow((object_id, object_name))


def clear_temp_dirs():
    for dir_name in ("archives", "xmls"):
        shutil.rmtree(dir_name)


def main():
    make_dirs(("archives", "xmls"))
    make_archives()
    levels, objects = collect_objects_data()
    save_csv(levels, objects)
    clear_temp_dirs()


if __name__ == "__main__":
    main()
