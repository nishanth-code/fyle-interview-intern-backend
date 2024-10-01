-- Write query to get number of graded assignments for each student:
SELECT COUNT(*) FROM ASSIGNMENTS WHERE state = "GRADED" group by student_id