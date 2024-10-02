from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment,AssignmentStateEnum
from core.models.teachers import Teacher
from core.libs import assertions,exceptions

from .schema import AssignmentSchema, AssignmentSubmitSchema,AssignmentGradeSchema
from ..teachers.schema import TeacherSchema

principal_assignment_resources = Blueprint('principal_assignment_resources', __name__)

@principal_assignment_resources.route('/assignments',methods=['GET'],strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    assignments = Assignment.get_all_assignments()
    assignments_dump = AssignmentSchema().dump(assignments,many=True)
    return APIResponse.respond(data=assignments_dump)

@principal_assignment_resources.route('/assignments/grade',methods=['POST'],strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_assignment(p,incoming_payload):
    grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)
    # aise exceptions.FyleError(400,"cannot grade assignments in draft state")
    marked_assignment = Assignment.mark_grade_principal(_id=grade_assignment_payload.id,grade=grade_assignment_payload.grade,auth_principal=p)
    db.session.commit()
    graded_assignment_dump = AssignmentSchema().dump(marked_assignment)
    return APIResponse.respond(data=graded_assignment_dump)



