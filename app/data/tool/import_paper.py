import os
import sys

from app.data.dao.paper_dao import PaperDAO
from app.data.dao.paper_section_dao import PaperSectionDAO
from app.data.dao.question_dao import QuestionDAO
from app.data.dao.question_group_dao import QuestionGroupDAO
from app.data.dao.question_option import QuestionOptionDAO
from app.data.dto.paper_dto import PaperDTO

file_name: str = 'paper_sample.md'

def import_paper():
    paper_dto = PaperDTO().md_parse(file_name)
    print(f'Parse paper {paper_dto.paper_id}: {len(paper_dto.sections)} sections, {len(paper_dto.question_groups)} question groups, {len(paper_dto.questions)} questions')
    paper = paper_dto.to_entity()
    paper_id = PaperDAO().add_or_update(paper)
    print(f'Save paper to Database: {paper_id}')

    for section_dto in paper_dto.sections:
        if section_dto.question_type is None and paper.question_type is not None:
            section_dto.question_type = paper.question_type
        if section_dto.unit_score is None and paper.unit_score is not None:
            section_dto.unit_score = paper.unit_score
        section = section_dto.to_entity()
        paper_section_id = PaperSectionDAO().add_or_update(section)
        print(f'## Save section to Database: {section_dto.name}, {paper_section_id}')

        for question_group_dto in section_dto.question_groups:
            if question_group_dto.question_type is None and section_dto.question_type is not None:
                question_group_dto.question_type = section_dto.question_type
            if question_group_dto.unit_score is None and section_dto.unit_score is not None:
                question_group_dto.unit_score = section_dto.unit_score
            question_group = question_group_dto.to_entity()
            question_group.section_id = paper_section_id
            question_group_id = QuestionGroupDAO().add_or_update(question_group)
            print(f'### Save question group to Database: {question_group_dto.title}')

            for question_dto in question_group_dto.questions:
                if question_dto.question_type is None and question_group_dto.question_type is not None:
                    question_dto.question_type = question_group_dto.question_type
                if question_dto.score is None and question_group_dto.unit_score is not None:
                    question_dto.score = question_group_dto.unit_score
                question = question_dto.to_entity()
                question.section_id = paper_section_id
                question.question_group_id = question_group_id
                question_dto.question_id = QuestionDAO().add_or_update(question)
                print(f'Save question to Database: {question_dto.seq}')
                for question_option_dto in question_dto.question_options:
                    question_option = question_option_dto.to_entity()
                    question_option.question_id = question_dto.question_id
                    QuestionOptionDAO().add_or_update(question_option)
                    print(f'- Save question option to Database: {question_option_dto.content}')

def main():
    import_paper()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
        print(f"[{os.getenv("ENV_STATE")} env] importing paper from {file_name}")
    main()