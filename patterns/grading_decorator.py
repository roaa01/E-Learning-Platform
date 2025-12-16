from models.assignment import Assignments, Submission

class Grader:
    """Component Interface"""
    def calculate_grade(self, submission: Submission, assignment: Assignments, raw_score: float) -> float:
        raise NotImplementedError

class BasicGrader(Grader):
    """Concrete Component"""
    def calculate_grade(self, submission: Submission, assignment: Assignments, raw_score: float) -> float:
        return raw_score

class GradeDecorator(Grader):
    """Base Decorator"""
    def __init__(self, grader: Grader):
        self._grader = grader

    def calculate_grade(self, submission: Submission, assignment: Assignments, raw_score: float) -> float:
        return self._grader.calculate_grade(submission, assignment, raw_score)

class LatePenaltyDecorator(GradeDecorator):
    """Concrete Decorator: Deducts 10% if submitted after due date"""
    def calculate_grade(self, submission: Submission, assignment: Assignments, raw_score: float) -> float:
        base_grade = self._grader.calculate_grade(submission, assignment, raw_score)
        
        if assignment.dueDate and submission.submittedDate > assignment.dueDate:
             penalty = assignment.maxGrade * 0.10
             print(f"Late submission! Deducting {penalty} points.")
             return max(0.0, base_grade - penalty)
        
        return base_grade
