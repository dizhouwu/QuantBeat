class ObjectCounter:
    counter = 0
    def __init__(self):
        type(self).counter +=1
    def __del__(self):
        type(self).counter -= 1

    @classmethod
    def count_live(cls):
        return cls.counter
    
class MyVector(ObjectCounter):
    pass

class MyCharStr(ObjectCounter):
    pass

v1, v2 = MyVector(), MyVector()
c1 = MyCharStr()
print(MyVector.count_live()) # 2
print(MyCharStr.count_live()) # 1
