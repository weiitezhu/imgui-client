class Pos:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Pos(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Pos(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return Pos(self.x * other.x, self.y * other.y)

    def __truediv__(self, other):
        return Pos(self.x / other.x, self.y / other.y)


class ScenePos(Pos):
    """场景坐标: 原点在画布中心， 会随画布大小而改变"""
    pass


class WorldPos(Pos):
    """世界坐标: 原点在左上角，会根据相机位置改变"""
    pass


class ViewPos(Pos):
    """视图坐标: 原点在左上角，不会随相机位置改变"""
    pass
