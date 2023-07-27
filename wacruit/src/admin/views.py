from typing import Any

from sqladmin import ModelView
from sqlalchemy import Column

from wacruit.src.admin.formatters import recruiting_formatter
from wacruit.src.admin.formatters import shorten_column
from wacruit.src.apps.announcement.models import Announcement
from wacruit.src.apps.problem.models import CodeSubmission
from wacruit.src.apps.problem.models import Problem
from wacruit.src.apps.problem.models import Testcase
from wacruit.src.apps.recruiting.models import Recruiting
from wacruit.src.apps.resume.models import ResumeQuestion
from wacruit.src.apps.resume.models import ResumeSubmission
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

    column_formatters = {Announcement.content: shorten_column(width=20)}


class RecruitingAdmin(ModelView, model=Recruiting):
    column_list = [
        Recruiting.id,
        Recruiting.name,
        Recruiting.is_active,
        Recruiting.from_date,
        Recruiting.to_date,
        Recruiting.description,
    ]

    column_formatters = {Recruiting.description: shorten_column(width=20)}


class ProblemAdmin(ModelView, model=Problem):
    column_list = [
        Problem.id,
        Problem.recruiting,
        Problem.num,
        Problem.body,
    ]

    column_formatters = {
        Problem.recruiting: recruiting_formatter,
        Problem.body: shorten_column(width=20),
    }


class CodeSubmissionAdmin(ModelView, model=CodeSubmission):
    @staticmethod
    def user_formatter(code_submission: type[CodeSubmission], attribute: Column[Any]):
        return code_submission.user.last_name + code_submission.user.first_name

    column_list = [
        CodeSubmission.id,
        CodeSubmission.user,
        CodeSubmission.problem,
        CodeSubmission.language,
        CodeSubmission.status,
        CodeSubmission.created_at,
    ]

    column_formatters = {
        CodeSubmission.user: user_formatter,
    }


class TestcaseAdmin(ModelView, model=Testcase):
    column_list = [
        Testcase.id,
        Testcase.problem,
        Testcase.time_limit,
        Testcase.extra_time,
        Testcase.memory_limit,
        Testcase.stack_limit,
        Testcase.is_example,
    ]

    column_formatters = {
        Testcase.stdin: shorten_column(),
        Testcase.expected_output: shorten_column(),
    }


class ResumeQuestionAdmin(ModelView, model=ResumeQuestion):
    column_list = [
        ResumeQuestion.id,
        ResumeQuestion.recruiting,
        ResumeQuestion.question_num,
        ResumeQuestion.content_limit,
        ResumeQuestion.content,
    ]

    column_formatters = {
        ResumeQuestion.recruiting: recruiting_formatter,
        ResumeQuestion.content: shorten_column(width=20),
    }


class ResumeSubmissionAdmin(ModelView, model=ResumeSubmission):
    @staticmethod
    def question_formatter(
        resume_submission: type[ResumeSubmission], attribute: Column[Any]
    ):
        return resume_submission.question.question_num

    column_list = [
        ResumeSubmission.id,
        ResumeSubmission.recruiting,
        ResumeSubmission.question,
    ]

    column_formatters = {
        ResumeSubmission.recruiting: recruiting_formatter,
        ResumeSubmission.question: question_formatter,
    }


admin_views = [
    UserAdmin,
    RecruitingAdmin,
    AnnouncementAdmin,
    ProblemAdmin,
    CodeSubmissionAdmin,
    TestcaseAdmin,
    ResumeQuestionAdmin,
    ResumeSubmissionAdmin,
]
