# -*- coding: utf-8 -*-

from related import immutable, IntegerField, StringField, FloatField, ChildField

from .._api_helper import FilterType
from .._endpoints import DATA_GRADE
from ..model import Serializable, DateTime, Teacher, Subject, Period


@immutable
class GradeCategory(Serializable):
    """A base grade category. Represents a generic type, like an exam, a short test,
    a homework or other ("current") grades.

    :var int ~.id: grade category's ID
    :var str ~.name: grade category's name
    :var str ~.code: grade category's code (e.g. short name or abbreviation)
    """

    id = IntegerField(key="Id")
    name = StringField(key="Name")
    code = StringField(key="Code")


@immutable
class GradeColumn(Serializable):
    """A grade column. Represents a topic which a student
    may get a grade from (e.g. a single exam, short test, homework).

    :var int ~.id: grade column's ID
    :var str ~.key: grade column's key (UUID)
    :var int ~.period_id: ID of the period when the grade is given
    :var str ~.name: grade column's name (description)
    :var str ~.code: grade column's code (e.g. short name or abbreviation)
    :var str ~.group: unknown, yet
    :var int ~.number: unknown, yet
    :var int ~.weight: weight of this column's grades
    :var `~vulcan.hebe.model.Subject` ~.subject: the subject from which
        grades in this column are given
    :var `~vulcan.hebe.data.GradeCategory` ~.category: category (base type)
        of grades in this column
    :var `~vulcan.hebe.model.Period` ~.period: a resolved period of this grade
    """

    id = IntegerField(key="Id")
    key = StringField(key="Key")
    period_id = IntegerField(key="PeriodId")
    name = StringField(key="Name")
    code = StringField(key="Code")
    group = StringField(key="Group")
    number = IntegerField(key="Number")
    weight = FloatField(key="Weight")
    subject = ChildField(Subject, key="Subject")
    category = ChildField(GradeCategory, key="Category")

    period = ChildField(Period, key="Period", required=False)


@immutable
class Grade(Serializable):
    """A grade.

    :var int ~.id: grade's ID
    :var int ~.pupil_id: the related pupil's ID
    :var str ~.content_raw: grade's content (with comment)
    :var str ~.content: grade's content (without comment)
    :var `~vulcan.hebe.model.DateTime` ~.date_created: grade's creation date
    :var `~vulcan.hebe.model.DateTime` ~.date_modified: grade's modification date
        (may be the same as ``date_created`` if it was never modified)
    :var `~vulcan.hebe.model.Teacher` ~.teacher_created: the teacher who added
        the grade
    :var `~vulcan.hebe.model.Teacher` ~.teacher_modified: the teacher who modified
        the grade
    :var `~vulcan.hebe.data.GradeColumn` ~.column: grade's column
    :var float ~.value: grade's value, may be `None` if 0.0
    :var str ~.comment: grade's comment, visible in parentheses in ``content_raw``
    :var float ~.numerator: for point grades: the numerator value
    :var float ~.denominator: for point grades: the denominator value
    """

    id = IntegerField(key="Id")
    pupil_id = IntegerField(key="PupilId")
    content_raw = StringField(key="ContentRaw")
    content = StringField(key="Content")
    date_created = ChildField(DateTime, key="DateCreated")
    date_modified = ChildField(DateTime, key="DateModify")
    teacher_created = ChildField(Teacher, key="Creator")
    teacher_modified = ChildField(Teacher, key="Modifier")
    column = ChildField(GradeColumn, key="Column")
    value = FloatField(key="Value", required=False)
    comment = StringField(key="Comment", required=False)
    numerator = FloatField(key="Numerator", required=False)
    denominator = FloatField(key="Denominator", required=False)

    @classmethod
    async def get(cls, api, last_sync, deleted, **kwargs):
        data = await api.helper.get_list(
            DATA_GRADE,
            FilterType.BY_PUPIL,
            deleted=deleted,
            last_sync=last_sync,
            **kwargs
        )

        for grade in data:
            grade["Column"]["Period"] = api.student.period_by_id(
                grade["Column"]["PeriodId"]
            ).as_dict
            yield Grade.load(grade)
