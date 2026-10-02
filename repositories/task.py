from sqlalchemy import select
from models.task import Task


class TaskRepository:
    def __init__(self, session):
        self.session = session

    def all(self, query=''):
        statement = select(Task)
        if query:
            statement = statement.where(Task.title.contains(query, autoescape=True))
        return self.session.scalars(statement.order_by(Task.created_at.desc(), Task.id.desc())).all()

    def get(self, identifier):
        return self.session.get(Task, identifier)

    def save(self, task):
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def delete(self, task):
        self.session.delete(task)
        self.session.commit()
