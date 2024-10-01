from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment

from .schema import AssignmentSchema, AssignmentSubmitSchema,AssignmentGradeSchema

principal_assignment_resources = Blueprint('principal_assignment_resources', __name__)

@principal_assignment_resources.route('/assignments',methods=['GET'],strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    assignments = Assignment.get_assignments_by_teacher()
    assignments_dump = AssignmentSchema().dump(assignments,many=True)
    return APIResponse.respond(data=assignments_dump)

@principal_assignment_resources.route('/assignments/grade',methods=['POST'],strict_slashes=False)
@decorators.authenticate_principal
def grade_assignment(p,incoming_payload):
    grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)
    marked_assignment = Assignment.mark_grade(_id=grade_assignment_payload.id,grade=grade_assignment_payload.grade,auth_principal=p)
    db.session.commit()
    return marked_assignment
