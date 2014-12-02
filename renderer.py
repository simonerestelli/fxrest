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


class Link(object):
	def __init__(self, path, rel = "self"):
		self.__path = path
		self.__rel = rel

	@property
	def data(self):
		return {
			"href": '/' + '/'.join(self.__path),
			"rel": self.__rel,
		}



def render(obj, expand = True):
	body = dict(obj.body)
	body["links"] = [Link(obj.path).data] + \
		map(lambda x: Link(x[1].path, "down").data,
			sorted(obj.children.items(), key = lambda x: x[0]))

	if expand and hasattr(obj, "entries"):
		body["entries"] = map(lambda x: render(x[1], expand = expand), obj.entries)
	return body

