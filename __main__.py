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

import json

import cherrypy

import fmwk
import renderer


class MyServer(object):
	def __init__(self, storage):
		self.__st = storage

	@cherrypy.expose
	def default(self, *args, **kwargs):
		req = cherrypy.request
		resp = cherrypy.response
		print args
		print
		status = 200
		try:
			if req.method == 'GET':
				obj = self.__st.get(args)
			if req.method == 'POST':
				obj = self.__st.post(args)
				status = 201
			if req.method == 'PUT':
				obj = self.__st.put(args)
			if req.method == 'DELETE':
				self.__st.delete(args)
				obj = None
				status = 204
		except fmwk.HTTPException as e:
			# TODO: return a body describing the error too
			raise cherrypy.HTTPError(e.httpCode)
		except KeyError:
			raise cherrypy.HTTPError(404)
		except NotImplementedError:
			# To play safe
			raise cherrypy.HTTPError(405)
		resp.headers['Content-Type'] = 'application/json'
		resp.status = status
		if obj is not None:
			body = renderer.render(obj)
			ret = json.dumps(body)
		else:
			ret = ''
		return ret


if __name__ == '__main__':
	st = fmwk.Storage()
	cherrypy.config.update({'server.socket_host': '0.0.0.0'})
	cherrypy.quickstart(MyServer(st))

