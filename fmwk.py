###############################################################
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
###############################################################

import UserDict


class HTTPException(BaseException):
	httpCode = 500

class BadRequest(HTTPException): httpCode = 400
class NotFound(HTTPException): httpCode = 404
class MethodNotAllowed(HTTPException): httpCode = 405



class _BaseNode(object):
	#status = 200
	def __init__(self, parent = None, body = {}, objectId = None):
		#self.__path = path
		self.__parent = parent
		self.__id = objectId
		self.__children = {}
		self._body = body

	def addChild(self, key, obj):
		key = str(key)
		# Do not want to overwrite existing children
		if key in self.__children:
			raise BadRequest()
		self.__children[key] = obj

	def delete(self, *args, **kwargs): raise MethodNotAllowed()
	def update(self, *args, **kwargs): raise MethodNotAllowed()
	def create(self, *args, **kwargs): raise MethodNotAllowed()

	def _lines(self, indent = 0):
		ret = []
		for k, v in sorted(self.children.items(), key = lambda x: x[0]):
			ret.append(' ' * indent + str(k))
			ret += v._lines(toStr(indent + 2))
		return ret

	@property
	def body(self):
		return self._body

	@property
	def id(self):
		return self.__id

	@property
	def path(self):
		ret = []
		curr = self
		while curr.__parent is not None:
			ret.insert(0, str(curr.id))
			curr = curr.__parent
		return ret

	@property
	def children(self):
		return self.__children



# Uri that is created through a POST
# Allow: GET, PUT, DELETE
class _Entry(_BaseNode):
	def __init__(self, body, **kwargs):
		super(_Entry, self).__init__(body = body, **kwargs)

	def update(self, body, partial = True):
		if partial:
			# TODO
			def _up(a, b):
				for k, v in b.iteritems():
					_up(a[k], v)
		else:
			self._body = body



# Allow only POST, PUT, GET, DELETE
class _Collection(_BaseNode):
	def __init__(self, **kwargs):
		super(_Collection, self).__init__(**kwargs)
		self.__nextId = 0

	def create(self, body):
		ret = _Entry(body, parent = self, objectId = self.__nextId)
		ret.status = 201
		self.children[str(self.__nextId)] = ret
		self.__nextId += 1
		return ret

	def addChild(self, key, obj):
		if not isinstance(obj, _Entry):
			raise BadRequest("Cannot add a suburi to a Collection manually")
		super(_Collection, self).addChild(key, obj)

	# TODO: overwrite the whole collection
	def update(self, body):
		raise NotImplementedError()

	@property
	def entries(self):
		return sorted(obj.children.items(), key = lambda x: x[0])


class _Node(_BaseNode):
	def __init__(self, **kwargs):
		super(_Node, self).__init__(**kwargs)

	def _create(self, path, index, body):
		curr = path[index]
		l = len(path)
		if curr not in self.children:
			if index < l - 1:
				newNode = _Node(parent = self, objectId = curr)
			else:
				newNode = _Collection(parent = self, objectId = curr)
			self.children[curr] = newNode

		return self.children[path[index]]._create(path, index + 1, body)



class Storage(object):
	def __init__(self):
		self.__data = {}
		self.__root = _BaseNode()

	def _resolvePath(self, path):
		curr = self.__root
		print path
		try:
			for x in path:
				curr = curr.children[x]
		except KeyError:
			# This will be mapped to a 404
			raise NotFound(path)
		return curr

	def get(self, path):
		return self._resolvePath(path)

	# TODO: perform some checks before deleting
	def delete(self, path):
		obj = self._resolvePath(path[:-1])
		del obj.children[path[-1]]

	def post(self, path, body = {}):
		curr = self.__root
		for x in path[:-1]:
			curr = curr.children.setdefault(x, _BaseNode(parent = curr, objectId = x))

		if path[-1] not in curr.children:
			coll = _Collection(parent = curr, objectId = path[-1])
			curr.children[path[-1]] = coll
		coll = curr.children[path[-1]]
		return coll.create(body)

	def _toStr(self):
		l = self.__root._toStr()
		print '\n'.join(l)

