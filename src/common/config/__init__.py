import pymongo
from pymongo.collection import Collection

from dataclasses import dataclass
from typing import Any, Optional


class BotConfig:
    __config_mongo: Optional[Collection] = None

    @classmethod
    def _get_config_mongo(cls) -> Collection:
        if cls.__config_mongo is None:
            mongo_client = pymongo.MongoClient('127.0.0.1', 27017, w=0)
            mongo_db = mongo_client['PallasBot']
            cls.__config_mongo = mongo_db['config']
            cls.__config_mongo.create_index(name='accounts_index',
                                            keys=[('account', pymongo.HASHED)])
        return cls.__config_mongo

    def __init__(self, bot_id: int) -> None:
        self.bot_id = bot_id
        self._mongo_find_key = {
            'account': bot_id
        }

    def _find_key(self, key: str) -> Any:
        info = self._get_config_mongo().find_one(self._mongo_find_key)
        if info and key in info:
            return info[key]
        else:
            return None

    def security(self) -> bool:
        '''
        账号是否安全（不处于风控等异常状态）
        '''
        security = self._find_key('security')
        return security if security is not None else False

    def auto_accept(self) -> bool:
        '''
        是否自动接受加群、加好友请求
        '''
        accept = self._find_key('auto_accept')
        return accept if accept is not None else False

    def is_admin(self, user_id: int) -> bool:
        '''
        是否是管理员
        '''
        admins = self._find_key('admins')
        return user_id in admins if admins is not None else False

    def add_admin(self, user_id: int) -> None:
        '''
        添加管理员
        '''
        self._get_config_mongo().update_one(
            self._mongo_find_key,
            {'$push': {'admins': user_id}},
            upsert=True
        )
