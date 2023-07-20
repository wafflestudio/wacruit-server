from wacruit.src.apps.problem.models import Problem
from wacruit.src.apps.problem.repositories import ProblemRepository


def test_only_show_example_testcase(
    problem: Problem, problem_repository: ProblemRepository
):
    p1 = problem_repository.get_problem_by_id_with_example(problem.id)
    assert p1 is not None
    assert p1.testcases[0].is_example is True


def test_get_testcases_by_problem_id(
    problem: Problem, problem_repository: ProblemRepository
):
    examples = problem_repository.get_testcases_by_problem_id(
        problem.id, is_example=True
    )
    assert examples[0].is_example is True
    reals = problem_repository.get_testcases_by_problem_id(problem.id, is_example=False)
    assert reals[0].is_example is False
