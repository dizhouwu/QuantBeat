#include <vector>
#include <format>
#include <iostream>

template <class Derived>
class ObjectCounter {
private:
	static inline size_t count{ 0 };

protected:
	ObjectCounter() { ++count; }
	ObjectCounter(const ObjectCounter&) { ++count; }
	ObjectCounter(ObjectCounter&&) { ++count; }
	~ObjectCounter() { --count; }

public:
	static std::size_t CountLive() { return count; }
};

template <typename T>
class MyVector : public ObjectCounter<MyVector<T>> {};

class MyCharString : public ObjectCounter<MyCharString> {};

int main() {
	MyVector<int> v1, v2;
	MyCharString s1;


	std::cout <<std::format("number of MyVector: {}\n", MyVector<int>::CountLive());
	std::cout<<std::format("number of myCharString: {}\n", MyCharString::CountLive());
	return 0;
}

