from sqladmin import ModelView

from wacruit.src.apps.announcement.models import Announcement
from wacruit.src.apps.problem.models import CodeSubmission
from wacruit.src.apps.problem.models import Problem
from wacruit.src.apps.problem.models import TestCase
from wacruit.src.apps.recruiting.models import Recruiting
from wacruit.src.apps.resume.models import ResumeQuestion
from wacruit.src.apps.resume.models import ResumeSubmission
from wacruit.src.apps.user.models import User


def recruiting_formatter(table, field):
    return table.recruiting and table.recruiting.name


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


class RecruitingAdmin(ModelView, model=Recruiting):
    column_list = [
        Recruiting.id,
        Recruiting.name,
        Recruiting.is_active,
        Recruiting.from_date,
        Recruiting.to_date,
        Recruiting.description,
    ]


class ProblemAdmin(ModelView, model=Problem):
    column_list = [
        Problem.id,
        Problem.recruiting,
        Problem.num,
        Problem.body,
    ]

    column_formatters = {Problem.recruiting: recruiting_formatter}


class CodeSubmissionAdmin(ModelView, model=CodeSubmission):
    @staticmethod
    def user_formatter(table: type[CodeSubmission], field):
        return table.user.last_name + table.user.first_name

    column_list = [
        CodeSubmission.id,
        CodeSubmission.user,
        CodeSubmission.problem,
        CodeSubmission.language,
        CodeSubmission.status,
        CodeSubmission.create_at,
    ]

    column_formatters = {
        CodeSubmission.user: user_formatter,
    }


class TestCaseAdmin(ModelView, model=TestCase):
    column_list = [
        TestCase.id,
        TestCase.problem,
        TestCase.is_example,
    ]


class ResumeQuestionAdmin(ModelView, model=ResumeQuestion):
    column_list = [
        ResumeQuestion.id,
        ResumeQuestion.recruiting,
        ResumeQuestion.question_num,
        ResumeQuestion.content_limit,
        ResumeQuestion.content,
    ]

    column_formatters = {ResumeQuestion.recruiting: recruiting_formatter}


class ResumeSubmissionAdmin(ModelView, model=ResumeSubmission):
    @staticmethod
    def question_formatter(table: type[ResumeSubmission], field):
        return table.question.question_num

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
    TestCaseAdmin,
    ResumeQuestionAdmin,
    ResumeSubmissionAdmin,
]
