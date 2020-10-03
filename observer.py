
import logging
from copy import deepcopy

from helpers import LOGW_NAME
logger = logging.getLogger(f'{__name__:{LOGW_NAME}}')


class Observable():

    def __init__(self, parent=None):
        self.parent = parent
        self._modified_children = set()
        self._modified = False

    def unmodified(self, obj=None):
        if not obj:
            if not self._modified:
                return
            self._modified = False
            obj = self
        else:
            self._modified_children.discard(id(obj))
        logger.debug(f'unmodified {obj}')
        if self.parent:
            self.parent.unmodified(obj)

    def modified(self, obj=None):
        if not obj:
            if self._modified:
                return
            self._modified = True
            obj = self
        else:
            self._modified_children.add(id(obj))
        # logger.info(f'modified {obj}')
        if self.parent:
            self.parent.modified(obj)

    def has_modifications(self):
        return self._modified or self._modified_children

    def modified_symbol(self):
        return '\u25CF' if self.has_modifications() else ' '

    def __copy__(self):
        logger.debug(f'copy {self}')
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo):
        logger.debug(f'deepcopy {self}')
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            #  print(k,v)
            if k == 'parent':
                #  because parent points up at entire hierarchy,
                #  ignore during copy
                setattr(result, k, None)
            else:
                setattr(result, k, deepcopy(v, memo))
        return result
