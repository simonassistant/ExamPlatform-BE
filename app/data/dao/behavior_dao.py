from app.data.dao.base_dao import BaseDAO
from app.data.entity.entities import Behavior


class BehaviorDAO(BaseDAO):
    def __init__(self):
        super().__init__(Behavior)
