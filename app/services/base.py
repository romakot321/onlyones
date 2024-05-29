import uuid
from typing import TypedDict

from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response
from fastapi import status
from fastapi.params import Depends as DependsClass
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import exc
from sqlalchemy import ScalarResult
from sqlalchemy import select
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import InstrumentedAttribute as TableAttr

from app.db.base import Base as BaseTable
from app.db.base import get_session


class TableAttributeWithSubqueryLoad(TypedDict):
    parent: TableAttr
    children: list[TableAttr]


TableAttributesType = TableAttr | TableAttributeWithSubqueryLoad | list[
    TableAttr | TableAttributeWithSubqueryLoad
]


class BaseService:
    base_table: BaseTable

    def __init__(
            self,
            response: Response = Response,
            session: AsyncSession = Depends(get_session)
    ):
        self.response = response
        self._session_creator = None
        self.session = None
        self._commit_and_close = False
        if not isinstance(session, DependsClass):
            self.session = session
            self._commit_and_close = True

    async def get(self, *args) -> BaseTable:
        raise NotImplementedError

    async def _get_list(
            self,
            page: int = 0,
            count: int = 1000,
            select_in_load: TableAttributesType | None = None,
            order_by_id: bool = True,
            **filters
    ) -> ScalarResult[BaseTable]:
        query = self._get_list_query(page, count, select_in_load, order_by_id, **filters)
        return await self.session.scalars(query)

    def _get_list_query(
            self,
            page: int = 0,
            count: int = 1000,
            select_in_load: TableAttributesType | None = None,
            order_by_id: bool = True,
            **filters
    ) -> Select:
        offset = page * count
        query = select(self.base_table)
        if select_in_load is not None:
            query = self._query_select_in_load(query, select_in_load)
        if order_by_id:
            query = query.order_by(self.base_table.id.desc())
        query = query.offset(offset).limit(count)
        query = self._query_filter(query, **filters)
        return query

    @staticmethod
    def _query_select_in_load(
            query: Select,
            table_attributes: TableAttributesType
    ) -> Select:
        if not isinstance(table_attributes, list):
            table_attributes = [table_attributes]
        select_in_loads = []
        for table_attr in table_attributes:
            if isinstance(table_attr, dict):
                select_in_load = selectinload(table_attr['parent'])
                for table_attr_child in table_attr['children']:
                    select_in_load.subqueryload(table_attr_child)
                select_in_loads.append(select_in_load)
            else:
                select_in_loads.append(selectinload(table_attr))
        query = query.options(
            *select_in_loads
        )
        return query

    def _select_in_load(
            self,
            select_in_load: TableAttributesType
    ) -> Select:
        query = select(self.base_table)
        return self._query_select_in_load(query, select_in_load)

    async def _get_one(
            self,
            select_in_load: TableAttributesType | None = None,
            mute_not_found_exception: bool = False,
            **filters
    ) -> BaseTable:
        query = self._filter(**filters)
        if select_in_load is not None:
            query = self._query_select_in_load(query, select_in_load)
        obj = await self.session.scalar(query)

        if obj is None and not mute_not_found_exception:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        return obj

    def _filter(self, **kwargs) -> Select:
        query = select(self.base_table)
        return self._query_filter(query, **kwargs)

    def _like_filter(self, **kwargs) -> Select:
        query = select(self.base_table)
        return self._query_like_filter(query, **kwargs)

    def _query_like_filter(self, query, **kwargs):
        for key, value in kwargs.items():
            if value is None:
                continue
            filter_ = '%{}%'.format(value)
            query = query.filter(getattr(self.base_table, key).like(filter_))
        return query

    @staticmethod
    def _query_filter(query, **kwargs):
        for key, value in kwargs.items():
            if value is not None:
                query = query.filter_by(**{key: value})
        return query

    async def commit(self):
        if not self._commit_and_close:
            return
        try:
            await self.session.commit()
        except exc.IntegrityError as e:
            await self.session.rollback()
            logger.exception(e)
            if 'is not present in table' in str(e.orig):
                table_name = str(e.orig).split('is not present in table')[1].strip().capitalize()
                table_name = table_name.strip('"').strip("'")
                raise HTTPException(status_code=404, detail=f'{table_name} not found')
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    async def _update(
            self,
            object_id,
            object_schema: BaseModel | dict | None = None,
            write_none: bool = False,
            **kwargs
    ) -> BaseTable:
        obj = await self.get(id=object_id)
        await self._update_obj(obj, object_schema, write_none, **kwargs)
        return await self.get(id=object_id)

    async def _update_obj(
            self,
            obj: BaseTable,
            object_schema: BaseModel | dict | None = None,
            write_none: bool = False,
            **kwargs
    ) -> BaseTable:
        if object_schema is None:
            object_schema = {}
        elif isinstance(object_schema, BaseModel):
            object_schema = object_schema.model_dump()

        modified = False
        for key, value in (object_schema | kwargs).items():
            attr = getattr(obj, key)
            if not write_none and value is None:
                continue
            field_is_modified = attr != value
            setattr(obj, key, value)

            modified = modified or field_is_modified
        self.session.add(obj)
        await self.commit()
        if not modified:
            self.response.status_code = status.HTTP_304_NOT_MODIFIED
        return obj

    async def _create(
            self,
            object_schema: BaseModel | None = None,
            **kwargs
    ) -> BaseTable:
        obj_dict = {}
        if object_schema is not None:
            obj_dict = object_schema.model_dump()

        obj = self.base_table(
            **obj_dict, **kwargs
        )

        self.session.add(obj)
        await self.commit()
        await self.session.refresh(obj)
        self.response.status_code = status.HTTP_201_CREATED
        return obj

    async def _delete(self, object_id):
        obj = await self.get(id=object_id)
        await self._delete_obj(obj)

    async def _delete_obj(self, obj: BaseTable):
        await self.session.delete(obj)
        await self.commit()
        self.response.status_code = status.HTTP_204_NO_CONTENT

    async def __aenter__(self):
        if self.session is None:
            self._session_creator = get_session()
            self.session = await anext(self._session_creator)
            self._commit_and_close = True
        return self

    async def __aexit__(self, *exc_info):
        if self._commit_and_close:
            try:
                self.session = await anext(self._session_creator)
            except StopAsyncIteration:
                pass

    async def child(
            self,
            response: Response | None = None,
            session: AsyncSession | None = None
    ):
        if session is not None:
            self.session = session
            self._commit_and_close = False
        if response is not None:
            self.response = response
        return self
