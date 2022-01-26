from asyncore import dispatcher
from ctypes import util
from multiprocessing.managers import BaseProxy, RemoteError, BaseManager
import threading


def convert_to_error(kind, result):
    if kind == '#ERROR':
        return result
    elif kind in ('#TRACEBACK', '#UNSERIALIZABLE'):
        if not isinstance(result, str):
            raise TypeError(
                "Result {0!r} (kind '{1}') type is {2}, not str".format(
                    result, kind, type(result)))
        if kind == '#UNSERIALIZABLE':
            return RemoteError('Unserializable message: %s\n' % result)
        else:
            return RemoteError(result)
    else:
        return ValueError('Unrecognized message type {!r}'.format(kind))


def _callmethod(self, methodname, args=(), kwds={}):
    '''
    Try to call a method of the referent and return a copy of the result
    '''
    try:
        conn = self._tls.connection
    except AttributeError:
        util.debug('thread %r does not own a connection',
                    threading.current_thread().name)
        self._connect()
        conn = self._tls.connection

    while True:
        try:
            conn.send((self._id, methodname, args, kwds))
            kind, result = conn.recv()
            break
        except (EOFError, BrokenPipeError) as e:
            print('正在重试连接')
            self._connect()

    if kind == '#RETURN':
        return result
    elif kind == '#PROXY':
        exposed, token = result
        proxytype = self._manager._registry[token.typeid][-1]
        token.address = self._token.address
        proxy = proxytype(
            token, self._serializer, manager=self._manager,
            authkey=self._authkey, exposed=exposed
            )
        conn = self._Client(token.address, authkey=self._authkey)
        dispatcher(conn, None, 'decref', (token.id,))
        return proxy
    raise convert_to_error(kind, result)


BaseProxy._callmethod = _callmethod


class MyManager(BaseManager):
    pass