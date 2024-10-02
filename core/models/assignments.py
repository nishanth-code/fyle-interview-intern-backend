import enum
from flask import abort
from core import db
from core.apis.decorators import AuthPrincipal
from core.libs import helpers, assertions
from core.models.teachers import Teacher
from core.models.students import Student
from sqlalchemy.types import Enum as BaseEnum
# from .exceptions import FyleError


class GradeEnum(str, enum.Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'


class AssignmentStateEnum(str, enum.Enum):
    DRAFT = 'DRAFT'
    SUBMITTED = 'SUBMITTED'
    GRADED = 'GRADED'


class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, db.Sequence('assignments_id_seq'), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey(Student.id), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey(Teacher.id), nullable=True)
    content = db.Column(db.Text)
    grade = db.Column(BaseEnum(GradeEnum))
    state = db.Column(BaseEnum(AssignmentStateEnum), default=AssignmentStateEnum.DRAFT, nullable=False)
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=helpers.get_utc_now, nullable=False)
    updated_at = db.Column(db.TIMESTAMP(timezone=True), default=helpers.get_utc_now, nullable=False, onupdate=helpers.get_utc_now)

    def __repr__(self):
        return '<Assignment %r>' % self.id

    @classmethod
    def filter(cls, *criterion):
        db_query = db.session.query(cls)
        return db_query.filter(*criterion)

    @classmethod
    def get_by_id(cls, _id):
        return cls.filter(cls.id == _id).first()

    @classmethod
    def upsert(cls, assignment_new: 'Assignment'):
        print("hello",assignment_new)
        if assignment_new.id is not None :
            assignment = Assignment.get_by_id(assignment_new.id)
            assertions.assert_found(assignment, 'No assignment with this id was found')
            assertions.assert_valid(assignment.state == 'DRAFT','only assignment in draft state can be edited')
            # assertions.assert_valid(assignment_new.content is not None , "empty assignment cannot be submited")
        elif assignment_new.content == None:
            assertions.base_assert(400,'empty assignment cannot be submite')
            assignment.content = assignment_new.content
        else:
            assignment = assignment_new
            db.session.add(assignment_new)

        db.session.flush()
        return assignment

    @classmethod
    def submit(cls, _id, teacher_id, auth_principal: AuthPrincipal):
        assignment = Assignment.get_by_id(_id)
        assertions.assert_found(assignment, 'No assignment with this id was found')
        assertions.assert_valid(assignment.student_id == auth_principal.student_id, 'This assignment belongs to some other student')
       
        if assignment.content  == None :
            assertions.base_assert(400,"content cannot be empty")
            

        # assertions.assert_valid(assignment.state  'SUBMITTED','only a draft assignment can be submitted')
        elif assignment.state == 'SUBMITTED':
            assertions.base_assert(400,"only a draft assignment can be submitted")
            


        assignment.teacher_id = teacher_id
        assignment.state = AssignmentStateEnum.SUBMITTED
        db.session.flush()

        return assignment


    @classmethod
    def mark_grade(cls, _id, grade, auth_principal: AuthPrincipal):
        assignment = Assignment.get_by_id(_id)
        
        assertions.assert_found(assignment, 'No assignment with this id was found')
        assertions.assert_valid(grade is not None, 'assignment with empty grade cannot be graded')
        assertions.assert_valid(assignment.state == 'SUBMITTED', ' only submitted assignemnts can be graded')
        assertions.assert_valid(assignment.teacher_id == auth_principal.teacher_id , "cross grading is not allowed")
    
        # if  assignment.state == AssignmentStateEnum.DRAFT:
        #     return abort(400,"")
            
        assignment.grade = grade
        if assignment.state != AssignmentStateEnum.DRAFT.value:
            assignment.grade = grade
            assignment.state = AssignmentStateEnum.GRADED
        db.session.flush()

        return assignment
    @classmethod
    def mark_grade_principal(cls, _id, grade, auth_principal: AuthPrincipal):
        assignment = Assignment.get_by_id(_id)
        #assertions.assert_found(assignment, 'No assignment with this id was found')
        #assertions.assert_valid(grade is not None, 'assignment with empty grade cannot be graded')
        # assertions.assert_valid(assignment.state != 'DRAFT', ' only submitted assignemnts can be graded')
        # assertions.assert_valid(assignment.teacher_id == auth_principal.teacher_id , "cross grading is not allowed")
        if assignment.state == 'DRAFT':
            assertions.base_assert(400," only submitted assignemnts can be graded")
        elif assignment.state == 'SUBMITTED' or assignment.state == 'GRADED' :
            assignment.grade = grade
            assignment.state = AssignmentStateEnum.GRADED
            db.session.flush()
            return assignment
       
        

    @classmethod
    def get_assignments_by_student(cls, student_id):
        return cls.filter(cls.student_id == student_id).all()

    @classmethod
    def get_assignments_by_teacher(cls,teacher_id):
        return cls.filter(cls.teacher_id == teacher_id , cls.state != AssignmentStateEnum.DRAFT).all()
    
    @classmethod
    def get_all_assignments(cls):
        return cls.filter(cls.state != AssignmentStateEnum.DRAFT).all()
