from .Machine.FakeOS import WriteRequest, SystemError

class Window:
	def __init__(self, x: int, y: int, id: str):
		self._x = x
		self._y = y
		self._id = id

		resp = WriteRequest(
			{
				"type": "AllocateWindow",
				"data": {
					'x': x,
					'y': y,
					"id": id
				}
			}
		)

		if resp["code"] != 2: raise SystemError(resp["value"])

	def Delete(self):
		WriteRequest(
			{
				"type": "DeAllocateWindow",
				"data": {
					"id": self.id
				}
			}
		)

	def AddText(self, text: str, x: int, y: int, size: int, color: str="black"):
		resp = WriteRequest(
			{
				"type": "Window.AddText",
				"data": {
					"id": self.id,
					"text": text,
					'x': x,
					'y': y,
					"size": size,
					"color": color
				}
			}
		)

		if resp["code"] != 1: raise SystemError(resp["value"])

		# have the resp return a callback/handle that can be used to 
		# remove or delete the text


	def __del__(self):
		self.Delete()

	@property
	def x(self): return self._x

	@property
	def y(self): return self._y

	@property
	def id(self): return self._id