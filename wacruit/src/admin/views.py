from typing import Any, Self

from sqladmin import ModelView

from wacruit.src.apps.announcement.models import Announcement
from wacruit.src.apps.problem.models import CodeSubmission
from wacruit.src.apps.problem.models import Problem
from wacruit.src.apps.problem.models import TestCase
from wacruit.src.apps.user.models import User


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.is_admin,
        User.first_name,
        User.last_name,
        User.email,
        User.phone_number,
        User.department,
        User.university,
        User.college,
    ]


class AnnouncementAdmin(ModelView, model=Announcement):
    column_list = [
        Announcement.id,
        Announcement.title,
        Announcement.content,
        Announcement.created_at,
        Announcement.updated_at,
    ]


class ProblemAdmin(ModelView, model=Problem):
    column_list = [
        Problem.id,
        Problem.body,
        Problem.submissions,
        Problem.testcases,
    ]


class CodeSubmissionAdmin(ModelView, model=CodeSubmission):
    @staticmethod
    def user_formatter(table: type[CodeSubmission], field):
        return table.user.last_name + table.user.first_name

    column_list = [
        CodeSubmission.id,
        CodeSubmission.user,
        CodeSubmission.problem_id,
        CodeSubmission.problem,
        CodeSubmission.create_at,
    ]

    column_formatters = {
        CodeSubmission.user: user_formatter,
    }


class TestCaseAdmin(ModelView, model=TestCase):
    column_list = [
        TestCase.id,
        TestCase.problem_id,
        TestCase.problem,
        TestCase.is_example,
    ]


admin_views = [
    UserAdmin,
    AnnouncementAdmin,
    ProblemAdmin,
    CodeSubmissionAdmin,
    TestCaseAdmin,
]
