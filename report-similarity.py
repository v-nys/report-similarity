import click  # type: ignore
import pathlib
import logging
import pymupdf # type: ignore
import functools
from jinja2 import Environment, FileSystemLoader, select_autoescape  # type: ignore
import strsimpy  # type: ignore
from bs4 import BeautifulSoup # type: ignore
import re
from spellchecker import SpellChecker # type: ignore

logging.basicConfig(filename="textsimilarity.log", level=logging.INFO)
env = Environment(loader=FileSystemLoader("."), autoescape=select_autoescape())


@functools.cache
def extract_text(path: pathlib.Path) -> str:
    if path.suffix == ".pdf":
        document = pymupdf.open(path)
        text = "\n".join((page.get_text() for page in document))
        return text
    else:
        raise ValueError("Unsupported file type.")


@click.command
@click.argument("assignments-folder", type=str, required=True)
@click.option("--language", type=str, default="nl")
def check_similarity(assignments_folder: str, language: str) -> None:
    spell_checker = SpellChecker(language=language)
    calculator = strsimpy.NormalizedLevenshtein()
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
                specific_comparison_remarks: list[str] = []
                if student_1_folder.name not in remarks:
                    remarks[student_1_folder.name] = {}
                remarks[student_1_folder.name][student_2_folder.name] = (
                    similarity,
                    specific_comparison_remarks,
                )
                if student_1_text.lower().strip() == student_2_text.lower().strip():
                    specific_comparison_remarks.append(
                        "Teksten zijn identiek (eventueel op hoofdletters en whitespace na)."
                    )
                else:
                    logging.info(student_1_text)
                    logging.info(student_2_text)
                    student_1_words = set(re.findall(r'\b[a-z]+\b', student_1_text.lower()))
                    #logging.info(student_1_words)
                    student_2_words = set(re.findall(r'\b[a-z]+\b', student_2_text.lower()))
                    #logging.info(student_2_words)
                    lexicon_intersection = student_1_words & student_2_words
                    unknown_lexicon = spell_checker.unknown(lexicon_intersection)
                    for word in unknown_lexicon:
                        specific_comparison_remarks.append(f"Gemeenschappelijk niet-woord: {word}")
            else:
                logging.warning(
                    f"Multiple (or 0) files in student folder {student_2_path}."
                )
        else:
            logging.warning(
                f"Multiple (or 0) files in student folder {student_1_path}."
            )
    matrix_template = env.get_template("matrixtemplate.html")
    # key needs to be present
    remarks[student_folders[-1].name] = {}
    soup = BeautifulSoup(matrix_template.render(remarks=remarks), "html.parser")
    print(soup.prettify())


if __name__ == "__main__":
    check_similarity()
