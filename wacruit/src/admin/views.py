from typing import Any

from sqladmin import ModelView
from sqlalchemy import Column

from wacruit.src.admin.formatters import recruiting_formatter
from wacruit.src.admin.formatters import shorten_column
from wacruit.src.admin.formatters import user_formatter
from wacruit.src.apps.announcement.models import Announcement
from wacruit.src.apps.problem.models import CodeSubmission
from wacruit.src.apps.problem.models import Problem
from wacruit.src.apps.problem.models import Testcase
from wacruit.src.apps.recruiting.models import Recruiting
from wacruit.src.apps.recruiting.models import RecruitingApplication
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

    form_excluded_columns = [
        User.code_submissions,
        User.resume_submissions,
        User.application,
    ]

    column_searchable_list = [
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
        Announcement.pinned,
        Announcement.created_at,
        Announcement.updated_at,
    ]

    column_formatters = {Announcement.content: shorten_column(width=20)}

    form_excluded_columns = [
        Announcement.created_at,
        Announcement.updated_at,
    ]

    column_searchable_list = [
        Announcement.title,
        Announcement.content,
    ]


class RecruitingAdmin(ModelView, model=Recruiting):
    column_list = [
        Recruiting.id,
        Recruiting.type,
        Recruiting.name,
        Recruiting.is_active,
        Recruiting.from_date,
        Recruiting.to_date,
        Recruiting.description,
        Recruiting.short_description,
    ]

    column_formatters = {
        Recruiting.description: shorten_column(width=20),  # type: ignore
        Recruiting.short_description: shorten_column(width=20),  # type: ignore
    }

    form_excluded_columns = [
        Recruiting.resume_submissions,
        Recruiting.resume_questions,
        Recruiting.problems,
        Recruiting.applicants,
    ]

    column_searchable_list = [
        Recruiting.name,
        Recruiting.description,
    ]


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

    form_excluded_columns = [
        Problem.submissions,
        Problem.code_submissions,
        Problem.testcases,
    ]

    column_searchable_list = [
        Problem.num,
        Problem.body,
    ]


class CodeSubmissionAdmin(ModelView, model=CodeSubmission):
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

    form_excluded_columns = [
        CodeSubmission.results,
        CodeSubmission.created_at,
    ]

    column_searchable_list = [
        CodeSubmission.user_id,
        CodeSubmission.language,
        CodeSubmission.status,
    ]


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

    form_excluded_columns = [
        Testcase.submission_results,
    ]

    column_searchable_list = [
        Testcase.problem_id,
        Testcase.stdin,
        Testcase.expected_output,
    ]


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

    form_excluded_columns = [
        ResumeQuestion.created_at,
        ResumeQuestion.updated_at,
        ResumeQuestion.resume_submissions,
    ]

    column_searchable_list = [
        ResumeQuestion.question_num,
        ResumeQuestion.content,
    ]


class ResumeSubmissionAdmin(ModelView, model=ResumeSubmission):
    @staticmethod
    def question_formatter(
        resume_submission: type[ResumeSubmission], attribute: Column[Any]
    ):
        question = getattr(resume_submission, "question")
        return question and question.question_num

    column_list = [
        ResumeSubmission.id,
        ResumeSubmission.recruiting,
        ResumeSubmission.question,
    ]

    column_formatters = {
        ResumeSubmission.recruiting: recruiting_formatter,
        ResumeSubmission.question: question_formatter,
    }

    form_excluded_columns = [
        ResumeSubmission.created_at,
        ResumeSubmission.updated_at,
    ]

    column_searchable_list = [
        ResumeSubmission.user_id,
        ResumeSubmission.answer,
    ]


class RecruitingApplicationAdmin(ModelView, model=RecruitingApplication):
    column_list = [
        RecruitingApplication.id,
        RecruitingApplication.recruiting,
        RecruitingApplication.user,
        RecruitingApplication.status,
        RecruitingApplication.created_at,
    ]

    column_formatters = {
        RecruitingApplication.recruiting: recruiting_formatter,
        RecruitingApplication.user: user_formatter,
    }

    form_excluded_columns = [
        RecruitingApplication.created_at,
        RecruitingApplication.updated_at,
    ]


admin_views = [
    UserAdmin,
    RecruitingAdmin,
    AnnouncementAdmin,
    ProblemAdmin,
    CodeSubmissionAdmin,
    TestcaseAdmin,
    ResumeQuestionAdmin,
    ResumeSubmissionAdmin,
    RecruitingApplicationAdmin,
]
