import pandas as pd
from django.db import connection

sql_query = lambda version: f"""
SELECT s.code AS "Student code",
       s.first_name AS "First name",
       s.last_name AS "Last name",
       e.name AS "Exam",
       SUM(m.points) AS "Points"
    FROM ipho_marking_marking AS m
    JOIN ipho_exam_participant_students AS ps ON m.participant_id = ps.participant_id
    JOIN ipho_core_student AS s ON s.id = ps.student_id
    JOIN ipho_exam_participant AS p ON p.id = ps.participant_id
    JOIN ipho_exam_exam AS e ON e.id = p.exam_id
    WHERE {version}
    GROUP BY GROUPING SETS (
        (e.name, s.code, s.first_name, s.last_name),
        (s.code, s.first_name, s.last_name)
);
"""


def get_version_marks(versions):
    """Obtains marks for different versions.

    Currently only works for a single version.

    Args:
        versions (list): can contain 'D' (delegation), 'O' (organizer),
            'F' (final)

    Returns:
        pd.DataFrame: table with results
    """
    assert len(versions) == 1
    query_string = f"m.version = '{versions[0]}'"
    rows, column_names = execute_sql(sql_query(query_string))
    exam = column_names[-2]
    points = column_names[-1]
    df = pd.DataFrame(rows, columns=column_names)
    df = df.pivot(index=column_names[:-2], columns=exam, values=points)
    # The grouping set SQL command places no value in the total points
    # column
    df.columns = df.columns.fillna("Total")
    return df


def execute_sql(sql_string):
    """Executes a raw SQL query and returns rows and column names."""
    with connection.cursor() as cursor:
        cursor.execute(sql_string)
        rows = cursor.fetchall()
        column_names = [col[0] for col in cursor.description]
    return rows, column_names
