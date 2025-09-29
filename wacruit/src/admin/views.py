from typing import Any

from sqladmin import ModelView
from sqlalchemy import Column
from wtforms import TextAreaField

from wacruit.src.admin.formatters import member_formatter
from wacruit.src.admin.formatters import project_urls_formatter
from wacruit.src.admin.formatters import recruiting_formatter
from wacruit.src.admin.formatters import shorten_column
from wacruit.src.admin.formatters import timeline_category_formatter
from wacruit.src.admin.formatters import user_formatter
from wacruit.src.apps.announcement.models import Announcement
from wacruit.src.apps.faq.models import FAQ
from wacruit.src.apps.history.models import History
from wacruit.src.apps.member.models import Member
from wacruit.src.apps.pre_registration.models import PreRegistration
from wacruit.src.apps.problem.models import CodeSubmission
from wacruit.src.apps.problem.models import Problem
from wacruit.src.apps.problem.models import Testcase
from wacruit.src.apps.project.models import Project
from wacruit.src.apps.project.models import ProjectURL
from wacruit.src.apps.recruiting.models import Recruiting
from wacruit.src.apps.recruiting.models import RecruitingApplication
from wacruit.src.apps.recruiting_info.models import RecruitingInfo
from wacruit.src.apps.resume.models import ResumeQuestion
from wacruit.src.apps.resume.models import ResumeSubmission
from wacruit.src.apps.review.models import Review
from wacruit.src.apps.seminar.models import Seminar
from wacruit.src.apps.sponsor.models import Sponsor
from wacruit.src.apps.timeline.models import Timeline
from wacruit.src.apps.timeline.models import TimelineCategory
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

    column_sortable_list = User.__table__.columns.keys()


class AnnouncementAdmin(ModelView, model=Announcement):
    column_list = [
        Announcement.id,
        Announcement.title,
        Announcement.content,
        Announcement.pinned,
        Announcement.created_at,
        Announcement.updated_at,
    ]

    column_formatters = {Announcement.content: shorten_column(width=20)}  # type: ignore

    form_excluded_columns = [
        Announcement.created_at,
        Announcement.updated_at,
    ]

    column_searchable_list = [
        Announcement.title,
        Announcement.content,
    ]

    column_sortable_list = Announcement.__table__.columns.keys()


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
        Recruiting.recruiting_info,
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

    column_sortable_list = Recruiting.__table__.columns.keys()


class ProblemAdmin(ModelView, model=Problem):
    column_list = [
        Problem.id,
        Problem.recruiting,
        Problem.num,
        Problem.body,
    ]

    column_formatters = {
        Problem.recruiting: recruiting_formatter,  # type: ignore
        Problem.body: shorten_column(width=20),  # type: ignore
    }

    form_excluded_columns = [
        Problem.submissions,
        Problem.code_submissions,
        Problem.testcases,
    ]

    column_searchable_list = [
        Problem.num,
        Problem.body,
        "recruiting.name",
    ]

    column_sortable_list = Problem.__table__.columns.keys()


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
        CodeSubmission.user: user_formatter,  # type: ignore
    }

    form_excluded_columns = [
        CodeSubmission.results,
        CodeSubmission.created_at,
    ]

    column_searchable_list = [
        CodeSubmission.user_id,
        CodeSubmission.language,
        CodeSubmission.status,
        "user.first_name",
    ]

    column_sortable_list = CodeSubmission.__table__.columns.keys()


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
        Testcase.stdin: shorten_column(),  # type: ignore
        Testcase.expected_output: shorten_column(),  # type: ignore
    }

    form_overrides = {"stdin": TextAreaField, "expected_output": TextAreaField}

    form_excluded_columns = [
        Testcase.submission_results,
    ]

    column_searchable_list = [
        Testcase.problem_id,
        Testcase.stdin,
        Testcase.expected_output,
    ]

    column_sortable_list = Testcase.__table__.columns.keys()


class ResumeQuestionAdmin(ModelView, model=ResumeQuestion):
    column_list = [
        ResumeQuestion.id,
        ResumeQuestion.recruiting,
        ResumeQuestion.question_num,
        ResumeQuestion.content_limit,
        ResumeQuestion.content,
    ]

    column_formatters = {
        ResumeQuestion.recruiting: recruiting_formatter,  # type: ignore
        ResumeQuestion.content: shorten_column(width=20),  # type: ignore
    }

    form_excluded_columns = [
        ResumeQuestion.created_at,
        ResumeQuestion.updated_at,
        ResumeQuestion.resume_submissions,
    ]

    column_searchable_list = [
        ResumeQuestion.question_num,
        ResumeQuestion.content,
        "recruiting.name",
    ]

    column_sortable_list = ResumeQuestion.__table__.columns.keys()


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
        ResumeSubmission.recruiting: recruiting_formatter,  # type: ignore
        ResumeSubmission.question: question_formatter,  # type: ignore
    }

    form_excluded_columns = [
        ResumeSubmission.created_at,
        ResumeSubmission.updated_at,
    ]

    column_searchable_list = [
        ResumeSubmission.user_id,
        ResumeSubmission.answer,
        "user.first_name",
        "recruiting.name",
    ]

    column_sortable_list = ResumeSubmission.__table__.columns.keys()


class RecruitingApplicationAdmin(ModelView, model=RecruitingApplication):
    column_list = [
        RecruitingApplication.id,
        RecruitingApplication.recruiting,
        RecruitingApplication.user,
        RecruitingApplication.status,
        RecruitingApplication.created_at,
    ]

    column_formatters = {
        RecruitingApplication.recruiting: recruiting_formatter,  # type: ignore
        RecruitingApplication.user: user_formatter,  # type: ignore
    }

    form_excluded_columns = [
        RecruitingApplication.created_at,
        RecruitingApplication.updated_at,
    ]

    column_searchable_list = [
        RecruitingApplication.user_id,
        RecruitingApplication.status,
        "user.first_name",
        "recruiting.name",
    ]

    column_sortable_list = RecruitingApplication.__table__.columns.keys()


class ProjectAdmin(ModelView, model=Project):
    column_list = [
        Project.id,
        Project.name,
        Project.summary,
        Project.introduction,
        Project.thumbnail_url,
        Project.project_type,
        Project.is_active,
        Project.formed_at,
        Project.urls,
    ]

    form_excluded_columns = [Project.images, Project.urls]

    column_formatters = {
        Project.urls: project_urls_formatter,  # type: ignore
    }

    column_searchable_list = [
        Project.name,
        Project.summary,
        Project.introduction,
    ]

    column_sortable_list = Project.__table__.columns.keys()


class ProjectURLAdmin(ModelView, model=ProjectURL):
    column_list = [
        ProjectURL.id,
        ProjectURL.url,
        ProjectURL.url_type,
        ProjectURL.project_id,
    ]

    form_columns = [ProjectURL.url, ProjectURL.url_type, ProjectURL.source_project]

    form_ajax_refs = {
        "source_project": {
            "fields": (Project.name,),
        }
    }

    column_sortable_list = ProjectURL.__table__.columns.keys()


class MemberAdmin(ModelView, model=Member):
    column_list = [
        Member.id,
        Member.first_name,
        Member.last_name,
        Member.introduction,
        Member.department,
        Member.college,
        Member.phone_number,
        Member.github_id,
        Member.generation,
        Member.is_active,
        Member.created_at,
        Member.position,
    ]

    column_searchable_list = [Member.first_name, Member.last_name]

    column_sortable_list = Member.__table__.columns.keys()


class ReviewAdmin(ModelView, model=Review):
    column_list = [
        Review.id,
        Review.member,
        Review.title,
        Review.content,
    ]

    column_formatters = {
        Review.member: member_formatter,  # type: ignore
    }

    column_searchable_list = [
        Review.title,
    ]

    column_sortable_list = Review.__table__.columns.keys()


class SeminarAdmin(ModelView, model=Seminar):
    column_list = [
        Seminar.id,
        Seminar.seminar_type,
        Seminar.curriculum_info,
        Seminar.prerequisite_info,
        Seminar.is_active,
    ]

    column_searchable_list = [Seminar.seminar_type]

    column_sortable_list = Seminar.__table__.columns.keys()


class PreRegistrationAdmin(ModelView, model=PreRegistration):
    column_list = [
        PreRegistration.id,
        PreRegistration.url,
        PreRegistration.generation,
        PreRegistration.is_active,
    ]
    column_searchable_list = [
        PreRegistration.url,
        PreRegistration.generation,
    ]

    column_sortable_list = PreRegistration.__table__.columns.keys()


class SponsorAdmin(ModelView, model=Sponsor):
    column_list = [
        Sponsor.id,
        Sponsor.name,
        Sponsor.amount,
        Sponsor.email,
        Sponsor.phone_number,
        Sponsor.sponsored_date,
    ]

    column_searchable_list = [
        Sponsor.name,
    ]

    column_sortable_list = Sponsor.__table__.columns.keys()


class TimelineAdmin(ModelView, model=Timeline):
    column_list = [
        Timeline.id,
        Timeline.title,
        Timeline.category,
        Timeline.group,
        Timeline.start_date,
        Timeline.end_date,
    ]
    column_formatters = {
        Timeline.category: timeline_category_formatter,  # type: ignore
    }
    column_searchable_list = [
        Timeline.title,
    ]

    column_sortable_list = Timeline.__table__.columns.keys()


class TimelineCategoryAdmin(ModelView, model=TimelineCategory):
    column_list = [
        TimelineCategory.id,
        TimelineCategory.title,
    ]

    column_searchable_list = [
        TimelineCategory.title,
    ]

    column_sortable_list = TimelineCategory.__table__.columns.keys()


class FAQAdmin(ModelView, model=FAQ):
    column_list = [
        FAQ.id,
        FAQ.question,
        FAQ.answer,
    ]

    column_searchable_list = [
        FAQ.question,
    ]

    column_sortable_list = FAQ.__table__.columns.keys()


class RecruitingInfoAdmin(ModelView, model=RecruitingInfo):
    column_list = [
        RecruitingInfo.id,
        RecruitingInfo.recruiting,
        RecruitingInfo.info_num,
    ]

    column_formatters = {
        RecruitingInfo.recruiting: recruiting_formatter  # type: ignore
    }

    column_searchable_list = [
        "recruiting.name",
        RecruitingInfo.info_num,
    ]

    column_sortable_list = RecruitingInfo.__table__.columns.keys()


class HistoryAdmin(ModelView, model=History):
    column_list = [
        History.id,
        History.history_key,
        History.history_value,
    ]

    column_searchable_list = [
        History.history_key,
    ]

    column_sortable_list = History.__table__.columns.keys()


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
    ProjectAdmin,
    ProjectURLAdmin,
    MemberAdmin,
    ReviewAdmin,
    SeminarAdmin,
    PreRegistrationAdmin,
    SponsorAdmin,
    TimelineAdmin,
    TimelineCategoryAdmin,
    FAQAdmin,
    RecruitingInfoAdmin,
    HistoryAdmin,
]
