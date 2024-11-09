import click  # type: ignore
import pathlib
import logging
import pypdf  # type: ignore
import functools
from jinja2 import Environment, FileSystemLoader, select_autoescape  # type: ignore
import strsimpy # type: ignore


logging.basicConfig(filename="textsimilarity.log", level=logging.INFO)
env = Environment(
    loader=FileSystemLoader("templates"), autoescape=select_autoescape()
)


@functools.cache
def extract_text(filename: pathlib.Path) -> str:
    return "test test"


@click.command
@click.argument("assignments-folder", type=str, required=True)
@click.option("--language", type=str, default="nl")
def check_similarity(assignments_folder: str) -> None:
    calculator = strsimpy.cosine.NormalizedStringDistance()
    remarks: dict[str, dict[str, tuple[float, list[str]]]] = {}
    assignments_path = pathlib.Path(assignments_folder)
    student_folders = sorted(
        [folder for folder in assignments_path.iterdir() if folder.is_dir()]
    )
    for student_1_folder_index, student_1_folder in enumerate(student_folders):
        student_1_path = assignments_path / student_1_folder.name
        student_1_file_paths = [
            entry for entry in student_1_path.iterdir() if entry.is_file()
        ]
        if len(student_1_file_paths) == 1:
            file_1_path = student_1_file_paths[0]
            student_1_text = extract_text(file_1_path)

        for student_2_folder_index, student_2_folder in enumerate(
            student_folders[student_1_folder_index + 1 :]
        ):
            student_2_path = assignments_path / student_2_folder.name
            student_2_file_paths = [
                entry for entry in student_2_path.iterdir() if entry.is_file()
            ]
            if len(student_2_file_paths) == 1:
                file_2_path = student_2_file_paths[0]
                student_2_text = extract_text(file_2_path)
                similarity = calculator.distance(student_1_text, student_2_text)
                remarks[student_1_folder.name][student_2_folder.name] = (similarity, [])
                # TODO: check for 100% identical contents and check for spelling mistakes
            else:
                logging.warning(
                    f"Multiple (or 0) files in student folder {student_2_path}."
                )
        else:
            logging.warning(
                f"Multiple (or 0) files in student folder {student_1_path}."
            )


if __name__ == "__main__":
    check_similarity()
