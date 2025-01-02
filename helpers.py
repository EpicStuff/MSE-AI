# Code copied from https://github.com/EpicStuff/python-EpicStuff/blob/main/src/epicstuff/dict.py, for reasons
from typing import Any, Mapping, MutableMapping


class Dict(dict):
	'''Basically a dictionary but you can access the keys as attributes (with a dot instead of brackets))

	you can also "bind" it to another `MutableMapping` object


	this is the old version, for when you got a target that you dont want to convert, say for example a CommentMap'''

	def __init__(self, target: MutableMapping | None = None) -> None:
		self._t = target or {}

	# make it so that the following functions are applied on the `._t`
	def __len__(self, *args, **kwargs): return self._t.__len__(*args, **kwargs)
	def __getitem__(self, *args, **kwargs): return self._t.__getitem__(*args, **kwargs)
	def __setitem__(self, *args, **kwargs): return self._t.__setitem__(*args, **kwargs)
	def __delitem__(self, *args, **kwargs): return self._t.__delitem__(*args, **kwargs)
	def __iter__(self, *args, **kwargs): return self._t.__iter__(*args, **kwargs)
	def __contains__(self, *args, **kwargs): return self._t.__contains__(*args, **kwargs)  # probably unnecessary
	def __reversed__(self, *args, **kwargs): return self._t.__reversed__(*args, **kwargs)
	def __or__(self, *args, **kwargs): return self._t.__or__(*args, **kwargs)
	def __ror__(self, *args, **kwargs): return self._t.__ror__(*args, **kwargs)
	def __ior__(self, *args, **kwargs): return self._t.__ior__(*args, **kwargs)

	# make it so that you can access the keys as attributes
	def __getattr__(self, *args, **kwargs) -> Any:
		'Run if `name` is not an attribute of `self`'
		# check (and run) if `name` is an attribute of `_t`  # trunk-ignore(ruff/ERA001)
		try:
			return self._t.__getattribute__(*args, **kwargs)
		# else
		except AttributeError:
			return self._t.__getitem__(*args, **kwargs)
	def __setattr__(self, name: str, value: Any) -> None:
		# TODO: maybe add recursive convert
		if name.startswith('_'):
			super().__setattr__(name, value)
		else:
			self._t[name] = value

	# stuff
	def __str__(self) -> str: return self._t.__str__()
	def __repr__(self) -> str: return f'{self.__class__.__name__}({self._t.__repr__()})'

	# maybe overcomplicated update function
	def update(self, __map: Mapping, overwrite: bool = True, **kwargs) -> None:
		if overwrite:
			self._t.update(__map | kwargs)
		else:
			for key, value in (__map | kwargs).items():
				self._t.setdefault(key, value)


OldDict = Dict

class Dict(dict):  # pylint: disable=function-redefined
	'''The class gives access to the dictionary through the attribute name.

	inspired by https://github.com/bstlabs/py-jdict and https://github.com/cdgriffith/Box

	pass _convert = False (`Dict(_convert=False)`) to use old dictionionary, behaves more like py-jdict
	set _convert to False (`Dict()._convert=False`) to disable the conversion of (nested) dicts to Dicts for future (after initialization) values that are added
	'''

	def __new__(cls, *args, _convert: bool = None, **kwargs) -> 'Dict':
		'''"redirects" to old dict if convert is False

		:param args: Any
		:param _convert: bool
		:param _create: bool
		:param kwargs: Any
		:return: Dict
		'''

		# if _convert was explicitly specified, pass it on
		if _convert is True:
			kwargs['_convert'] = True
		# if convert is False
		elif _convert is False:
			obj = OldDict.__new__(OldDict, *args, **kwargs)
			obj.__init__(*args, **kwargs)
			return obj
		return super().__new__(cls, *args, **kwargs)
	def __init__(self, *args, recursive_convert=True, **kwargs) -> None:
		super().__init__(*args, **kwargs)
		if recursive_convert:
			for key, value in self.items():
				self[key] = self.convert(value, key, True)
	def __getattr__(self, key: str) -> Any:
		'''Method returns the value of the named attribute of an object. If not found, it returns null object.

		:param name: str
		:return: Any
		'''
		# auto create nested Dict() if _create = True and not exist  # trunk-ignore(ruff/ERA001)
		if key not in self and '_create' in self and self._create:
			self[key] = Dict(_create=True)
		return self.__getitem__(key)
	def __setattr__(self, key: str, value: Any) -> None:
		'''Method sets the value of given attribute of an object.

		:param key: str
		:param value: Any
		:return: None
		'''
		self.__setitem__(key, value)
	def __delattr__(self, __name: str) -> None:
		# i think, not tested
		return super().__delitem__(__name)
	def __setitem__(self, key: Any, value: Any) -> None:
		# convert value to Dict before setting
		return super().__setitem__(key, self.convert(value, key))
	def __repr__(self) -> str: return f'{self.__class__.__name__}({super().__repr__()})'
	def convert(self, value: Any, key: Any = None, ignore__convert=False) -> Any:  # trunk-ignore(ruff/ARG002), pylint: disable=unused-argument
		'''Convert (nested) dicts in dicts or lists to Dicts

		:param value: Any
		:return: Any
		'''
		# if were not ignoring _convert and _convert is in self and _convert is False
		if not ignore__convert and '_convert' in self and not self._convert:
			pass
		elif isinstance(value, list):
			value = list(map(self.convert, value))
		elif isinstance(value, dict) and not isinstance(value, Dict):
			value = Dict(value)
		return value
