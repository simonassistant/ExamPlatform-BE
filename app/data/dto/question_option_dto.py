from app.data.entity.entities import QuestionOption


class QuestionOptionDTO:
    def __init__(self, **kwargs):
        self.question_option_id = kwargs.get('id')
        self.code = kwargs.get('code')
        self.content = kwargs.get('content')
        self.is_correct = kwargs.get('is_correct')
        self.correct_seq = kwargs.get('correct_seq')
        self.question_id = kwargs.get('question_id')
        self.paper_id = kwargs.get('paper_id')

    def md_parse_meta(self, content: str):
        lines = content.split('\n')
        for line in lines:
            data = line.split(':')
            if len(data) == 2:
                key = data[0].strip().lower()
                value = data[1].strip()
                if key == 'correct seq':
                    self.correct_seq = value

    def to_entity(self) -> QuestionOption:
        return QuestionOption(
            id = self.question_option_id,
            code = self.code,
            content = self.content,
            is_correct = self.is_correct,
            correct_seq = self.correct_seq,
            question_id = self.question_id,
            paper_id = self.paper_id
        )