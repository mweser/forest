# Copyright (c) 2022 MobileCoin Inc.
# Copyright (c) 2022 Ilia Daniher <i@mobilecoin.com>
# MIT LICENSE

import asyncio
import gzip
import hashlib
import json
import os
import time
from typing import Union, Any, Optional, cast, List, Generic, TypeVar

import aiohttp
import base58
from Crypto.Cipher import AES, _mode_eax

NAMESPACE = os.getenv("FLY_APP_NAME") or open("/etc/hostname").read().strip()
SALT = os.getenv("SALT", "ECmG8HtNNMWb4o2bzyMqCmPA6KTYJPCkd")
# build your AESKEY envvar with this: cat /dev/urandom | head -c 32 | base58
AESKEY = base58.b58decode(os.getenv("AESKEY", "kWKuomB9Ty3GcJ9yA1yED").encode()) * 2

if not AESKEY or len(AESKEY) not in [16, 32, 64]:
    raise ValueError(
        "Need to set 128b or 256b (16 or 32 byte) AESKEY envvar for persistence. It should be base58 encoded."
    )

if len(AESKEY) == 64:
    AESKEY = AESKEY[:32]

pAUTH = os.getenv("PAUTH", "")

if not pAUTH:
    raise ValueError("Need to set PAUTH envvar for persistence")


def encrypt(data: bytes, key: bytes) -> bytes:
    """Accepts data (as arbitrary length bytearray) and key (as 16B or 32B bytearray) and returns authenticated and encrypted blob (as bytearray)"""
    cipher = cast(_mode_eax.EaxMode, AES.new(key, AES.MODE_EAX))
    ciphertext, authtag = cipher.encrypt_and_digest(data)  # pylint: disable
    return cipher.nonce + authtag + ciphertext


def decrypt(data: bytes, key: bytes) -> bytes:
    """Accepts ciphertext (as arbitrary length bytearray) and key (as 16B or 32B bytearray) and returns decrypted (plaintext) blob (as bytearray)"""
    cipher = cast(_mode_eax.EaxMode, AES.new(key, AES.MODE_EAX, data[:16]))
    return cipher.decrypt_and_verify(data[32:], data[16:32])  # pylint: disable


def get_safe_key(key_: str) -> str:
    """returns a base58 encoded sha256sum of a salted key"""
    return base58.b58encode(hashlib.sha256(f"{SALT}{key_}".encode()).digest()).decode()


def get_safe_value(value_: Union[str, bytes]) -> str:
    """returns a base58 encoded aes128 AES EAX mode encrypted gzip compressed value"""
    if isinstance(value_, str):
        value_bytes = value_.encode()
    elif isinstance(value_, bytes):
        value_bytes = value_
    else:
        raise ValueError
    return base58.b58encode(encrypt(gzip.compress(value_bytes), AESKEY)).decode()


def get_cleartext_value(value_: str) -> str:
    """decrypts, decodes, decompresses a b58 blob returning cleartext"""
    return gzip.decompress(decrypt(base58.b58decode(value_), AESKEY)).decode()


class fastpKVStoreClient:
    """Strongly consistent, persistent storage.
    Stores a sneak table mapping keys to their existence to update faster.
    On top of Postgresql and Postgrest.
    Schema:
                                         Table "public.keyvalue"
       Column   |       Type       | Collation | Nullable |             Default
    ------------+------------------+-----------+----------+----------------------------------
     key        | bigint           |           | not null | generated by default as identity
     value      | text             |           |          | 'EMPTY'::text
     update     | text             |           |          |
     namespace  | text             |           |          |
     key_       | text             |           | not null |
     created_at | double precision |           |          |
     ttl        | bigint           |           |          |
     updated_at | double precision |           |          |
    Indexes:
        "keyvalue_pkey" PRIMARY KEY, btree (key)
        "keyvalue_key__key" UNIQUE CONSTRAINT, btree (key_)

    """

    def __init__(
        self,
        base_url: str = "https://vwaurvyhomqleagryqcc.supabase.co/rest/v1/keyvalue",
        auth_str: str = pAUTH,
        namespace: str = NAMESPACE,
    ):
        self.url = base_url
        self.conn = aiohttp.ClientSession()
        self.auth = auth_str
        self.namespace = get_safe_key(namespace)
        self.exists: dict[str, bool] = {}
        self.headers = {
            "Content-Type": "application/json",
            "apikey": f"{self.auth}",
            "Authorization": f"Bearer {self.auth}",
            "Prefer": "return=representation",
        }

    async def post(self, key: str, data: str) -> str:
        key = get_safe_key(key)
        data = get_safe_value(data)
        # try to set
        if self.exists.get(key):
            async with self.conn.patch(
                f"{self.url}?key_=eq.{key}&namespace=eq.{self.namespace}",
                headers=self.headers,
                data=json.dumps(
                    dict(
                        value=data,
                        updated_at=time.time(),
                        namespace=self.namespace,
                    )
                ),
            ) as resp:
                return await resp.json()
        async with self.conn.post(
            f"{self.url}",
            headers=self.headers,
            data=json.dumps(
                dict(
                    key_=key,
                    value=data,
                    created_at=time.time(),
                    namespace=self.namespace,
                )
            ),
        ) as resp:
            resp_text = await resp.text()
            # if set fails
            if "duplicate key value violates unique constraint" in resp_text:
                self.exists[key] = True
                # do update (patch not post)
                async with self.conn.patch(
                    f"{self.url}?key_=eq.{key}&namespace=eq.{self.namespace}",
                    headers=self.headers,
                    data=json.dumps(
                        dict(
                            value=data,
                            updated_at=time.time(),
                            namespace=self.namespace,
                        )
                    ),
                ) as resp:
                    return await resp.json()
            return json.loads(resp_text)

    async def get(self, key: str) -> str:
        """Get and return value of an object with the specified key and namespace"""
        key = get_safe_key(key)
        async with self.conn.get(
            f"{self.url}?select=value&key_=eq.{key}&namespace=eq.{self.namespace}",
            headers={
                "Accept": "application/octet-stream",
                "apikey": f"{self.auth}",
                "Authorization": f"Bearer {self.auth}",
            },
        ) as resp:
            maybe_res = await resp.text()
            if maybe_res:
                self.exists[key] = True
                return get_cleartext_value(maybe_res)
            return ""


K = TypeVar("K")
V = TypeVar("V", str, int, list[str], dict[str, str])


class aPersistDict(Generic[K, V]):
    """Async, consistent, persistent storage.
    Does not inherit from dict, but behaves mostly in the same way.
    Care is taken to offer asynchronous methods and strong consistency.
    This can be used for
        - inventory
        - subscribers
        - config info
    in a way that are persisted across reboots.
    No schemas and privacy preserving, but could be faster.
    Each write takes about 70 ms.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """If an argument is provided or a 'tag' keyword argument is passed...
        this will be used as a tag for backup / restore.
        """
        self.tag = ""
        if args:
            self.tag = args[0]
        if "tag" in kwargs:
            self.tag = kwargs.pop("tag")
        self.dict_: dict[K, Optional[V]] = {}
        self.client = fastpKVStoreClient()
        self.rwlock = asyncio.Lock()
        self.loop = asyncio.get_event_loop()
        self.init_task = asyncio.create_task(self.finish_init(**kwargs))
        self.write_task: Optional[asyncio.Task] = None

    def __repr__(self) -> str:
        return f"a{self.dict_}"

    def __str__(self) -> str:
        return f"a{self.dict_}"

    async def __getitem__(self, key: K) -> Optional[V]:
        return await self.get(key)

    def __setitem__(self, key: K, value: V) -> None:
        if self.write_task and not self.write_task.done():
            raise ValueError("Can't set value. write_task incomplete.")
        self.write_task = asyncio.create_task(self.set(key, value))

    async def finish_init(self, **kwargs: Any) -> None:
        """Does the asynchrnous part of the initialisation process."""
        async with self.rwlock:
            key = f"Persist_{self.tag}_{NAMESPACE}"
            result = await self.client.get(key)
            if result:
                self.dict_ = json.loads(result)
            self.dict_.update(**kwargs)

    async def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """Analogous to dict().get() - but async. Waits until writes have completed on the backend before returning results."""
        # always wait for pending writes - where a task has been created but lock not held
        if self.write_task:
            await self.write_task
            self.write_task = None
        # then grab the lock
        async with self.rwlock:
            return self.dict_.get(key, default)

    async def keys(self) -> List[K]:
        async with self.rwlock:
            return list(self.dict_.keys())

    async def remove(self, key: K) -> None:
        """Removes a value from the map, if it exists."""
        await self.set(key, None)
        return None

    # async def increment(self, key: K, value: V) -> str:
    #     """Since one cannot simply add to a coroutine, this function exists.
    #     If the key exists and the value is None, or an empty array, the provided value is added to a(the) list at that value."""
    #     value_to_extend = 0
    #     async with self.rwlock:
    #         value_to_extend = self.dict_.get(key, 0)
    #         return await self._set(key, value_to_extend + value)

    # async def decrement(self, key: K, value: V) -> str:
    #     """Since one cannot simply add to a coroutine, this function exists.
    #     If the key exists and the value is None, or an empty array, the provided value is added to a(the) list at that value."""
    #     value_to_extend = 0
    #     async with self.rwlock:
    #         value_to_extend = self.dict_.get(key, 0)
    #         return await self._set(key, value_to_extend - value)

    async def pop(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """Returns and removes a value if it exists"""
        res = await self.get(key, default)
        await self.set(key, None)
        return res

    async def _set(self, key: K, value: Optional[V]) -> str:
        """Sets a value at a given key, returns metadata.
        This function exists so *OTHER FUNCTIONS* holding the lock can set values."""
        if key is not None and value is not None:
            self.dict_.update({key: value})
        elif key and value is None and key in self.dict_:
            self.dict_.pop(key)
        client_key = f"Persist_{self.tag}_{NAMESPACE}"
        client_value = json.dumps(self.dict_)
        return await self.client.post(client_key, client_value)

    async def set(self, key: K, value: Optional[V]) -> str:
        """Sets a value at a given key, returns metadata."""
        async with self.rwlock:
            return await self._set(key, value)

    # async def extend(self, key: K, value: V) -> str:
    #     """Since one cannot simply add to a coroutine, this function exists.
    #     If the key exists and the value is None, or an empty array, the provided value is added to a(the) list at that value."""
    #     value_to_extend: Union[None, V, list[V]] = []
    #     async with self.rwlock:
    #         value_to_extend = self.dict_.get(key, [])
    #         if isinstance(value_to_extend, list):
    #             value_to_extend.append(value)
    #             return await self._set(key, value_to_extend)
    #         raise TypeError(f"value {value_to_extend} for key {key} is not a list")

    # async def remove_from(self, key: K, not_value: V) -> str:
    #     """Removes a value specified from the list, if present.
    #     Returns metadata"""
    #     async with self.rwlock:
    #         values_without_specified = [
    #             el for el in self.dict_.get(key, []) if not_value != el
    #         ]
    #         return await self._set(key, values_without_specified)
