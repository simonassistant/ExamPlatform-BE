DROP TABLE IF EXISTS users;
CREATE TABLE users(
    id VARCHAR(26) NOT NULL,
    username VARCHAR(64),
    pwd VARCHAR(255),
    email VARCHAR(64),
    mobile VARCHAR(64),
    surname VARCHAR(64),
    name VARCHAR(64),
    gender bool,
    enroll_number VARCHAR(20),
    is_examinee bool,
    is_proctor bool,
    created_by VARCHAR(26),
    created_at TIMESTAMP,
    updated_by VARCHAR(26),
    updated_at TIMESTAMP,
    is_deleted bool,
    PRIMARY KEY (id)
);

COMMENT ON TABLE users IS 'User';
COMMENT ON COLUMN users.id IS 'ID';
COMMENT ON COLUMN users.username IS 'Username';
COMMENT ON COLUMN users.pwd IS 'Password';
COMMENT ON COLUMN users.email IS 'Email';
COMMENT ON COLUMN users.mobile IS 'Mobile';
COMMENT ON COLUMN users.surname IS 'Surname';
COMMENT ON COLUMN users.name IS 'Name';
COMMENT ON COLUMN users.gender IS 'Gender;True: man; False: women';
COMMENT ON COLUMN users.enroll_number IS 'Enroll Number;student or staff number';
COMMENT ON COLUMN users.is_examinee IS 'Is Examinee';
COMMENT ON COLUMN users.is_proctor IS 'Is Proctor';
COMMENT ON COLUMN users.created_by IS 'Creator ID';
COMMENT ON COLUMN users.created_at IS 'Create Datetime';
COMMENT ON COLUMN users.updated_by IS 'Updator ID';
COMMENT ON COLUMN users.updated_at IS 'Update Datetime';
COMMENT ON COLUMN users.is_deleted IS 'Is Deleted';


CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE UNIQUE INDEX idx_users_enroll_number ON users(enroll_number);

DROP TABLE IF EXISTS behavior;
CREATE TABLE behavior(
    id VARCHAR(26) NOT NULL,
    user_id VARCHAR(26),
    ip VARCHAR(40),
    behavior_type VARCHAR(64),
    created_by VARCHAR(26),
    created_at TIMESTAMP,
    updated_by VARCHAR(26),
    updated_at TIMESTAMP,
    is_deleted VARCHAR,
    PRIMARY KEY (id)
);

COMMENT ON TABLE behavior IS '用户行为记录';
COMMENT ON COLUMN behavior.id IS 'ID';
COMMENT ON COLUMN behavior.user_id IS 'User ID';
COMMENT ON COLUMN behavior.ip IS 'IP';
COMMENT ON COLUMN behavior.behavior_type IS 'Behavior Type';
COMMENT ON COLUMN behavior.created_by IS 'Creator ID';
COMMENT ON COLUMN behavior.created_at IS 'Create Datetime';
COMMENT ON COLUMN behavior.updated_by IS 'Updator ID';
COMMENT ON COLUMN behavior.updated_at IS 'Update Datetime';
COMMENT ON COLUMN behavior.is_deleted IS 'Is Deleted';

DROP TABLE IF EXISTS schedule;
CREATE TABLE schedule(
    id VARCHAR(26) NOT NULL,
    title VARCHAR(255),
    created_by VARCHAR(26),
    created_at TIMESTAMP,
    updated_by VARCHAR(26),
    updated_at TIMESTAMP,
    is_deleted bool,
    PRIMARY KEY (id)
);

COMMENT ON TABLE schedule IS 'Schedule';
COMMENT ON COLUMN schedule.id IS 'ID';
COMMENT ON COLUMN schedule.title IS 'Schedule Title';
COMMENT ON COLUMN schedule.created_by IS 'Creator ID';
COMMENT ON COLUMN schedule.created_at IS 'Create Datetime';
COMMENT ON COLUMN schedule.updated_by IS 'Updator ID';
COMMENT ON COLUMN schedule.updated_at IS 'Update Datetime';
COMMENT ON COLUMN schedule.is_deleted IS 'Is Deleted';


CREATE INDEX idx_schedule_id_updated ON schedule(id,updated_at);

DROP TABLE IF EXISTS schedule_session;
CREATE TABLE schedule_session(
    id VARCHAR(26) NOT NULL,
    title VARCHAR(255),
    is_ready bool,
    plan_start TIMESTAMP,
    plan_end TIMESTAMP,
    place VARCHAR(255),
    proctor_email VARCHAR(255),
    proctor_id VARCHAR(26),
    paper_id VARCHAR(26),
    schedule_id VARCHAR(26),
    created_by VARCHAR(26),
    created_at TIMESTAMP,
    updated_by VARCHAR(26),
    updated_at TIMESTAMP,
    is_deleted bool,
    PRIMARY KEY (id)
);

COMMENT ON TABLE schedule_session IS 'Schedule Session';
COMMENT ON COLUMN schedule_session.id IS 'ID';
COMMENT ON COLUMN schedule_session.title IS 'Session Title';
COMMENT ON COLUMN schedule_session.is_ready IS 'Is Ready';
COMMENT ON COLUMN schedule_session.plan_start IS 'Plan Start Datetime';
COMMENT ON COLUMN schedule_session.plan_end IS 'Plan End Datetime';
COMMENT ON COLUMN schedule_session.place IS 'Examination Room';
COMMENT ON COLUMN schedule_session.proctor_email IS 'Proctor Email';
COMMENT ON COLUMN schedule_session.proctor_id IS 'Proctor ID';
COMMENT ON COLUMN schedule_session.paper_id IS 'Paper ID';
COMMENT ON COLUMN schedule_session.schedule_id IS 'Schedule ID';
COMMENT ON COLUMN schedule_session.created_by IS 'Creator ID';
COMMENT ON COLUMN schedule_session.created_at IS 'Create Datetime';
COMMENT ON COLUMN schedule_session.updated_by IS 'Updator ID';
COMMENT ON COLUMN schedule_session.updated_at IS 'Update Datetime';
COMMENT ON COLUMN schedule_session.is_deleted IS 'Is Deleted';


CREATE INDEX idx_schedule_session_paper_plan_start ON schedule_session(paper_id,plan_start);
CREATE INDEX idx_schedule_session_proctor_schedule_plan_start ON schedule_session(proctor_id,schedule_id,plan_start);

DROP TABLE IF EXISTS schedule_section;
CREATE TABLE schedule_section(
    id VARCHAR(26) NOT NULL,
    seq smallint,
    plan_start_early TIMESTAMP,
    plan_start_late TIMESTAMP,
    schedule_session_id VARCHAR(26),
    created_by VARCHAR(26),
    created_at TIMESTAMP,
    updated_by VARCHAR(26),
    updated_at TIMESTAMP,
    is_deleted VARCHAR,
    PRIMARY KEY (id)
);

COMMENT ON TABLE schedule_section IS 'Schedule Section';
COMMENT ON COLUMN schedule_section.id IS 'ID';
COMMENT ON COLUMN schedule_section.seq IS 'Sequence';
COMMENT ON COLUMN schedule_section.plan_start_early IS 'Plan Early Start Datetime';
COMMENT ON COLUMN schedule_section.plan_start_late IS 'Plan Late Start Datetime';
COMMENT ON COLUMN schedule_section.schedule_session_id IS 'Schedule Session ID';
COMMENT ON COLUMN schedule_section.created_by IS 'Creator ID';
COMMENT ON COLUMN schedule_section.created_at IS 'Create Datetime';
COMMENT ON COLUMN schedule_section.updated_by IS 'Updator ID';
COMMENT ON COLUMN schedule_section.updated_at IS 'Update Datetime';
COMMENT ON COLUMN schedule_section.is_deleted IS 'Is Deleted';


CREATE INDEX idx_schedule_section_schedule_session_seq ON schedule_section(schedule_session_id,seq);

DROP TABLE IF EXISTS exam;
CREATE TABLE exam(
    id VARCHAR(26) NOT NULL,
    token VARCHAR(64),
    status smallint,
    current_seq smallint,
    current_section VARCHAR(26),
    actual_start TIMESTAMP,
    actual_end TIMESTAMP,
    is_timeout bool,
    score NUMERIC(6,2),
    is_passed bool,
    examinee_enroll_number VARCHAR(20),
    examinee_email VARCHAR(255),
    examinee_id VARCHAR(26),
    paper_id VARCHAR(26),
    schedule_session_id VARCHAR(26),
    schedule_id VARCHAR(26),
    created_by VARCHAR(26),
    created_at TIMESTAMP,
    updated_by VARCHAR(26),
    updated_at TIMESTAMP,
    is_deleted bool,
    PRIMARY KEY (id)
);

COMMENT ON TABLE exam IS 'Exam';
COMMENT ON COLUMN exam.id IS 'ID';
COMMENT ON COLUMN exam.token IS 'Login Token';
COMMENT ON COLUMN exam.status IS 'Exam Status;0:No Access; 1:In Preparation; 2:In Exam; 3:Closed';
COMMENT ON COLUMN exam.current_seq IS 'Current Exam Section Sequence';
COMMENT ON COLUMN exam.current_section IS 'Current Exam Section';
COMMENT ON COLUMN exam.actual_start IS 'Actual Start Datetime';
COMMENT ON COLUMN exam.actual_end IS 'Actual End Datetime';
COMMENT ON COLUMN exam.is_timeout IS 'Is Exam Timeout';
COMMENT ON COLUMN exam.score IS 'Exam Score';
COMMENT ON COLUMN exam.is_passed IS 'Is Exam Passed';
COMMENT ON COLUMN exam.examinee_enroll_number IS 'examinee_enroll_number';
COMMENT ON COLUMN exam.examinee_email IS 'Examinee Email';
COMMENT ON COLUMN exam.examinee_id IS 'Examinee ID';
COMMENT ON COLUMN exam.paper_id IS 'Paper ID';
COMMENT ON COLUMN exam.schedule_session_id IS 'Schedule Session ID';
COMMENT ON COLUMN exam.schedule_id IS 'Schedule ID';
COMMENT ON COLUMN exam.created_by IS 'Creator ID';
COMMENT ON COLUMN exam.created_at IS 'Create Datetime';
COMMENT ON COLUMN exam.updated_by IS 'Updator ID';
COMMENT ON COLUMN exam.updated_at IS 'Update Datetime';
COMMENT ON COLUMN exam.is_deleted IS 'Is Deleted';


CREATE INDEX idx_exam_paper ON exam(paper_id);
CREATE INDEX idx_exam_examinee_status ON exam(examinee_id,status);
CREATE INDEX idx_exam_schedule_session_examinee ON exam(schedule_session_id,examinee_id);

DROP TABLE IF EXISTS exam_section;
CREATE TABLE exam_section(
    id VARCHAR(26) NOT NULL,
    name VARCHAR(20),
    seq smallint,
    status smallint,
    current_seq smallint,
    actual_start TIMESTAMP,
    actual_end TIMESTAMP,
    is_timeout bool,
    score NUMERIC(6,2),
    is_passed bool,
    examinee_id VARCHAR(26),
    exam_id VARCHAR(26),
    paper_id VARCHAR(26),
    paper_section_id VARCHAR(26),
    schedule_session_id VARCHAR(26),
    schedule_id VARCHAR(26),
    created_by VARCHAR(26),
    created_at TIMESTAMP,
    updated_by VARCHAR(26),
    updated_at TIMESTAMP,
    is_deleted bool,
    PRIMARY KEY (id)
);

COMMENT ON TABLE exam_section IS 'Exam Section';
COMMENT ON COLUMN exam_section.id IS 'ID';
COMMENT ON COLUMN exam_section.name IS 'Name;same as the name of paper section';
COMMENT ON COLUMN exam_section.seq IS 'Sequence';
COMMENT ON COLUMN exam_section.status IS 'Exam Status;0:No Access; 1:In Preparation; 2:In Exam; 3:Closed';
COMMENT ON COLUMN exam_section.current_seq IS 'Current Exam Answer Sequence';
COMMENT ON COLUMN exam_section.actual_start IS 'Actual Start Datetime';
COMMENT ON COLUMN exam_section.actual_end IS 'Actual End Datetime';
COMMENT ON COLUMN exam_section.is_timeout IS 'Is Exam Section Timeout';
COMMENT ON COLUMN exam_section.score IS 'Exam Section Score';
COMMENT ON COLUMN exam_section.is_passed IS 'Is Exam Section Passed';
COMMENT ON COLUMN exam_section.examinee_id IS 'Examinee ID';
COMMENT ON COLUMN exam_section.exam_id IS 'Exam ID';
COMMENT ON COLUMN exam_section.paper_id IS 'Paper ID';
COMMENT ON COLUMN exam_section.paper_section_id IS 'Paper Section ID';
COMMENT ON COLUMN exam_section.schedule_session_id IS 'Schedule Session ID';
COMMENT ON COLUMN exam_section.schedule_id IS 'Schedule ID';
COMMENT ON COLUMN exam_section.created_by IS 'Creator ID';
COMMENT ON COLUMN exam_section.created_at IS 'Create Datetime';
COMMENT ON COLUMN exam_section.updated_by IS 'Updator ID';
COMMENT ON COLUMN exam_section.updated_at IS 'Update Datetime';
COMMENT ON COLUMN exam_section.is_deleted IS 'Is Deleted';


CREATE INDEX idx_exam_section_exam_seq ON exam_section(exam_id,seq);
CREATE INDEX idx_exam_section_schedule_session_examinee_seq ON exam_section(schedule_session_id,examinee_id,seq);

DROP TABLE IF EXISTS exam_answer;
CREATE TABLE exam_answer(
    id VARCHAR(26) NOT NULL,
    seq smallint,
    answer TEXT,
    marked bool,
    is_correct smallint,
    score NUMERIC(6,2),
    question_group_id VARCHAR(26),
    question_id VARCHAR(26),
    examinee_id VARCHAR(26),
    exam_section_id VARCHAR(26),
    exam_id VARCHAR(26),
    created_by VARCHAR(26),
    created_at TIMESTAMP,
    updated_by VARCHAR(26),
    updated_at TIMESTAMP,
    is_deleted bool,
    PRIMARY KEY (id)
);

COMMENT ON TABLE exam_answer IS 'Exam Answer';
COMMENT ON COLUMN exam_answer.id IS 'ID';
COMMENT ON COLUMN exam_answer.seq IS 'Sequence';
COMMENT ON COLUMN exam_answer.answer IS 'Answer';
COMMENT ON COLUMN exam_answer.marked IS 'Marked for review';
COMMENT ON COLUMN exam_answer.is_correct IS 'Is Answer Correct;0:Wrong; 1:Half Correct; 2:All Correct';
COMMENT ON COLUMN exam_answer.score IS 'Exam Answer Score';
COMMENT ON COLUMN exam_answer.question_group_id IS 'Question Group';
COMMENT ON COLUMN exam_answer.question_id IS 'Question ID';
COMMENT ON COLUMN exam_answer.examinee_id IS 'Examinee ID';
COMMENT ON COLUMN exam_answer.exam_section_id IS 'Exam Section ID';
COMMENT ON COLUMN exam_answer.exam_id IS 'Exam ID';
COMMENT ON COLUMN exam_answer.created_by IS 'Creator ID';
COMMENT ON COLUMN exam_answer.created_at IS 'Create Datetime';
COMMENT ON COLUMN exam_answer.updated_by IS 'Updator ID';
COMMENT ON COLUMN exam_answer.updated_at IS 'Update Datetime';
COMMENT ON COLUMN exam_answer.is_deleted IS 'Is Deleted';

DROP TABLE IF EXISTS paper;
CREATE TABLE paper(
    id VARCHAR(26) NOT NULL,
    title VARCHAR(255),
    note TEXT,
    section_num smallint,
    question_num smallint,
    question_type smallint,
    unit_score NUMERIC(6,2),
    full_score NUMERIC(6,2),
    pass_score NUMERIC(6,2),
    duration smallint,
    created_by VARCHAR(26),
    created_at TIMESTAMP,
    updated_by VARCHAR(26),
    updated_at TIMESTAMP,
    is_deleted bool,
    PRIMARY KEY (id)
);

COMMENT ON TABLE paper IS 'Paper';
COMMENT ON COLUMN paper.id IS 'ID';
COMMENT ON COLUMN paper.title IS 'Paper Title';
COMMENT ON COLUMN paper.note IS 'Paper Note';
COMMENT ON COLUMN paper.section_num IS 'Section Num';
COMMENT ON COLUMN paper.question_num IS 'Question Num';
COMMENT ON COLUMN paper.question_type IS 'Question Type;1.single choice; 2.true-false; 3.definite multiple choice; 4.indefinite multiple choice; 5.fill-in-the-blank; 6.writing; 7.listening; 8.speaking';
COMMENT ON COLUMN paper.unit_score IS 'Unit/Question Score';
COMMENT ON COLUMN paper.full_score IS 'Full Score';
COMMENT ON COLUMN paper.pass_score IS 'Pass Score';
COMMENT ON COLUMN paper.duration IS 'Duration in Minutes';
COMMENT ON COLUMN paper.created_by IS 'Creator ID';
COMMENT ON COLUMN paper.created_at IS 'Create Datetime';
COMMENT ON COLUMN paper.updated_by IS 'Updator ID';
COMMENT ON COLUMN paper.updated_at IS 'Update Datetime';
COMMENT ON COLUMN paper.is_deleted IS 'Is Deleted';

DROP TABLE IF EXISTS paper_section;
CREATE TABLE paper_section(
    id VARCHAR(26) NOT NULL,
    seq smallint,
    name VARCHAR(20),
    duration smallint,
    question_num smallint,
    question_type smallint,
    unit_score NUMERIC(6,2),
    full_score NUMERIC(6,2),
    pass_score NUMERIC(6,2),
    note TEXT,
    paper_id VARCHAR(26),
    created_by VARCHAR(26),
    created_at TIMESTAMP,
    updated_by VARCHAR(26),
    updated_at TIMESTAMP,
    is_deleted bool,
    PRIMARY KEY (id)
);

COMMENT ON TABLE paper_section IS 'Paper Section';
COMMENT ON COLUMN paper_section.id IS 'ID';
COMMENT ON COLUMN paper_section.seq IS 'Sequence';
COMMENT ON COLUMN paper_section.name IS 'Name';
COMMENT ON COLUMN paper_section.duration IS 'Duration in Minutes';
COMMENT ON COLUMN paper_section.question_num IS 'Question Num';
COMMENT ON COLUMN paper_section.question_type IS 'Question Type;1.single choice; 2.true-false; 3.definite multiple choice; 4.indefinite multiple choice; 5.fill-in-the-blank; 6.writing; 7.listening; 8.speaking';
COMMENT ON COLUMN paper_section.unit_score IS 'Unit/Question Score';
COMMENT ON COLUMN paper_section.full_score IS 'Full Score';
COMMENT ON COLUMN paper_section.pass_score IS 'Pass Score';
COMMENT ON COLUMN paper_section.note IS 'Note';
COMMENT ON COLUMN paper_section.paper_id IS 'Paper ID';
COMMENT ON COLUMN paper_section.created_by IS 'Creator ID';
COMMENT ON COLUMN paper_section.created_at IS 'Create Datetime';
COMMENT ON COLUMN paper_section.updated_by IS 'Updator ID';
COMMENT ON COLUMN paper_section.updated_at IS 'Update Datetime';
COMMENT ON COLUMN paper_section.is_deleted IS 'Is Deleted';


CREATE INDEX idx_paper_section_paper_seq ON paper_section(paper_id,seq);

DROP TABLE IF EXISTS question;
CREATE TABLE question(
    id VARCHAR(26) NOT NULL,
    seq smallint,
    code VARCHAR(20),
    content TEXT,
    question_type smallint,
    score NUMERIC(6,2),
    question_group_id VARCHAR(26),
    section_id VARCHAR(26),
    paper_id VARCHAR(26),
    created_by VARCHAR(26),
    created_at TIMESTAMP,
    updated_by VARCHAR(26),
    updated_at TIMESTAMP,
    is_deleted bool,
    PRIMARY KEY (id)
);

COMMENT ON TABLE question IS 'Question';
COMMENT ON COLUMN question.id IS 'ID';
COMMENT ON COLUMN question.seq IS 'Sequence';
COMMENT ON COLUMN question.code IS 'Code';
COMMENT ON COLUMN question.content IS 'Content';
COMMENT ON COLUMN question.question_type IS 'Question Type;1.single choice; 2.true-false; 3.definite multiple choice; 4.indefinite multiple choice; 5.fill-in-the-blank; 6.writing; 7.listening; 8.speaking';
COMMENT ON COLUMN question.score IS 'Score';
COMMENT ON COLUMN question.question_group_id IS 'Question Group ID';
COMMENT ON COLUMN question.section_id IS 'Section ID';
COMMENT ON COLUMN question.paper_id IS 'Paper ID';
COMMENT ON COLUMN question.created_by IS 'Creator ID';
COMMENT ON COLUMN question.created_at IS 'Create Datetime';
COMMENT ON COLUMN question.updated_by IS 'Updator ID';
COMMENT ON COLUMN question.updated_at IS 'Update Datetime';
COMMENT ON COLUMN question.is_deleted IS 'Is Deleted';

DROP TABLE IF EXISTS question_group;
CREATE TABLE question_group(
    id VARCHAR(26) NOT NULL,
    seq smallint,
    code VARCHAR(20),
    title VARCHAR(255),
    content VARCHAR,
    question_type smallint,
    unit_score NUMERIC(6,2),
    full_score NUMERIC(6,2),
    section_id VARCHAR(26),
    paper_id VARCHAR(26),
    created_by VARCHAR(26),
    created_at TIMESTAMP,
    updated_by VARCHAR(26),
    updated_at TIMESTAMP,
    is_deleted bool,
    PRIMARY KEY (id)
);

COMMENT ON TABLE question_group IS 'Question Group';
COMMENT ON COLUMN question_group.id IS 'ID';
COMMENT ON COLUMN question_group.seq IS 'Sequence';
COMMENT ON COLUMN question_group.code IS 'Code';
COMMENT ON COLUMN question_group.title IS 'Title';
COMMENT ON COLUMN question_group.content IS 'Content';
COMMENT ON COLUMN question_group.question_type IS 'Question Type;1.single choice; 2.true-false; 3.definite multiple choice; 4.indefinite multiple choice; 5.fill-in-the-blank; 6.writing; 7.listening; 8.speaking';
COMMENT ON COLUMN question_group.unit_score IS 'Unit/Question Score';
COMMENT ON COLUMN question_group.full_score IS 'Full Score';
COMMENT ON COLUMN question_group.section_id IS 'Section ID';
COMMENT ON COLUMN question_group.paper_id IS 'Paper ID';
COMMENT ON COLUMN question_group.created_by IS 'Creator ID';
COMMENT ON COLUMN question_group.created_at IS 'Create Datetime';
COMMENT ON COLUMN question_group.updated_by IS 'Updator ID';
COMMENT ON COLUMN question_group.updated_at IS 'Update Datetime';
COMMENT ON COLUMN question_group.is_deleted IS 'Is Deleted';

DROP TABLE IF EXISTS question_option;
CREATE TABLE question_option(
    id VARCHAR(26) NOT NULL,
    code VARCHAR(1),
    content TEXT,
    is_correct bool,
    correct_seq smallint,
    question_id VARCHAR(26),
    paper_id VARCHAR(26),
    created_by VARCHAR(26),
    created_at TIMESTAMP,
    updated_by VARCHAR(26),
    updated_at TIMESTAMP,
    is_deleted bool,
    PRIMARY KEY (id)
);

COMMENT ON TABLE question_option IS 'Question Option';
COMMENT ON COLUMN question_option.id IS 'ID';
COMMENT ON COLUMN question_option.code IS 'Code/Sequence';
COMMENT ON COLUMN question_option.content IS 'Content';
COMMENT ON COLUMN question_option.is_correct IS 'Is This Option Correct';
COMMENT ON COLUMN question_option.correct_seq IS 'Sequence in correct answers';
COMMENT ON COLUMN question_option.question_id IS 'Question ID';
COMMENT ON COLUMN question_option.paper_id IS 'Paper ID';
COMMENT ON COLUMN question_option.created_by IS 'Creator ID';
COMMENT ON COLUMN question_option.created_at IS 'Create Datetime';
COMMENT ON COLUMN question_option.updated_by IS 'Updator ID';
COMMENT ON COLUMN question_option.updated_at IS 'Update Datetime';
COMMENT ON COLUMN question_option.is_deleted IS 'Is Deleted';

