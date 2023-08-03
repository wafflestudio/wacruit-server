from wacruit.src.apps.problem.models import Problem
from wacruit.src.apps.problem.services import ProblemService


def test_get_problem(problem_service: ProblemService, problem: Problem):
    problem_response = problem_service.get_problem(problem.id)
    assert problem_response.num == 1
    assert problem_response.body == "1번 문제입니다."
    assert len(problem_response.testcases) == 1

    testcase = problem_response.testcases[0]
    assert testcase.stdin == "example_input"
    assert testcase.expected_output == "example_output"
