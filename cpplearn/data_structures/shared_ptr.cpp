#include <algorithm>
#include <cstddef>
#include <memory>

namespace mp {
	template <class T> class shared_ptr;
    inline long atomic_inc(long volatile* addend) {
        return __sync_add_and_fetch(addend, 1);
    }
    inline long atomic_dec(long volatile* addend) {
        return __sync_sub_and_fetch(addend, 1);
    }

	// Base class of ref count, handle all the logic of ref count
	class RefCountBase {
		long ref_count_ = 1;
	public:
		RefCountBase(){
		}
		RefCountBase(const RefCountBase&) = delete;
		RefCountBase& operator=(const RefCountBase&) = delete;

		virtual ~RefCountBase(){
		}

		void Incref() {
			atomic_inc(&ref_count_);
		}
		void Decref() {
			if (atomic_dec(&ref_count_) == 0) {
				Destroy();
				// when refcount == 0. delete the object itself
				// so the owner needn't worry about when to releasing it
				DeleteThis();
			}
		}
		long UseCount() const {
			return ref_count_;
		}
		// destroy the resource
		virtual void Destroy() = 0;
		// destroy the object by itselfs
		virtual void DeleteThis() = 0;
	};

	// RefCount for pointer delete, use delete operator
	// the most common ref count
	template <class T>
	class RefCount : public RefCountBase {
		T* ptr_;
	public:
		RefCount(T* ptr) :ptr_(ptr) {

		}

		RefCount(const RefCount&) = delete;

		RefCount& operator=(RefCount&) = delete;

		virtual ~RefCount(){}

		virtual void Destroy() {
			delete ptr_;
			ptr_ = nullptr;
		}

		virtual void DeleteThis() {
			delete this;
		}
	};

    template <class T, class D>
    class RefCountDel: public RefCountBase {
    private:
        T* ptr_;
        D del_;
    public:
        RefCountDel(T* ptr, D del): ptr_(ptr), del_(del) {
        }

        RefCountDel(const RefCountDel&) = delete;

        RefCountDel& operator=(const RefCountDel&) = delete;

        virtual void Destroy() {
            del_(ptr_);
        }

        virtual void DeleteThis() {
            delete this;
        }
    };

    template <class T>
    class RefCountObj: public RefCountBase {
    private:
        typename std::aligned_storage<sizeof(T)>::type storage_;
    public:
        template<class... Types>
        RefCountObj(Types... args) {
            new (&storage_)T(std::forward<Types>(args)...);
        }

        T* Get() const {
            return (T*)(&storage_);
        }

        virtual void Destroy() {
            Get()->~T();
        }

        virtual void DeleteThis() {
            delete this;
        }
    };

    template <class T, class... Types>
    shared_ptr<T> make_shared(Types&&... args) {
        RefCountObj<T>* obj = new RefCountObj<T>(std::forward<Types>(args)...);
        shared_ptr<T> p;
        p.reset_ref_0(obj->Get(), obj);
        return p;
    }

	template <class T, class U>
	RefCountBase* CreateRefCount(shared_ptr<T>* /* for template parameter deduction */, U* p) {
		return new RefCount<T>(p);
	}

	template <class T>
	RefCountBase* CreateRefCount(shared_ptr<T[]>* /* for template parameter deduction */, T* p) {
		return new RefCountDel<T, std::default_delete<T[]>>(p, std::default_delete<T[]>());
	}

	template <class T>
	struct sp_element
	{
		typedef T type;
	};

	template <class T>
	struct sp_element<T[]>
	{
		typedef T type;
	};

	// shared_ptr
	// shared_ptr<string> p(new string("abc"));
	// shared_ptr<string> p2(p);
	template <class T>
	class shared_ptr {
	private:
		// if we use T* here and T is array type like int[], we'll have trouble
		typedef typename sp_element<T>::type element_type;
		RefCountBase* pref_;
		element_type* ptr_;
	public:
		shared_ptr() : pref_(nullptr), ptr_(nullptr) {
		}

		shared_ptr(element_type* ptr) : ptr_(ptr) {
			pref_ = CreateRefCount(this, ptr);
		}

		template<class U> explicit shared_ptr(U* ptr) :
			pref_(CreateRefCount(this, ptr)), ptr_(ptr) {
		}

		template<class U, class D> shared_ptr(U* ptr, D del) :
			pref_(new RefCountDel<U, D>(ptr, del)), ptr_(ptr) {
		}

		shared_ptr(std::nullptr_t) :pref_(nullptr), ptr_(nullptr) {
		}

        template<class D> shared_ptr(std::nullptr_t, D del) :
            pref_(new RefCountDel<T, D>(nullptr, del)), ptr_(nullptr) {
        }

		template<class U> shared_ptr(const shared_ptr<U>& u, T* ptr):
			pref_(nullptr), ptr_(nullptr){
			reset_ref(ptr, u.pref_);
		}

		shared_ptr(const shared_ptr& rhs):
			pref_(nullptr), ptr_(nullptr) {
			reset_ref(rhs.ptr_, rhs.pref_);
		}

		template<class U> shared_ptr(const shared_ptr<U>& rhs):
            ptr_(nullptr), pref_(nullptr) {
			reset_ref(rhs.ptr_, rhs.pref_);
		}

        // move ctor
		shared_ptr(shared_ptr&& rhs):
            pref_(rhs.pref_), ptr_(rhs.ptr_) {
			rhs.pref_ = nullptr;
			rhs.ptr_ = nullptr;
		}
		template <class U> shared_ptr(shared_ptr<U>&& rhs) : pref_(rhs.pref_), ptr_(rhs.ptr_) {
			rhs.pref_ = nullptr;
			rhs.ptr_ = nullptr;
		}

		shared_ptr& operator=(const shared_ptr& rhs) {
			reset_ref(rhs.ptr_, rhs.pref_);
			return *this;
		}

		shared_ptr& operator=(shared_ptr&& rhs) {
			reset_ref(rhs.ptr_, rhs.pref_);
			return *this;
		}

		template <class U>
		shared_ptr& operator=(shared_ptr<U>&& rhs) {
			reset_ref(rhs.ptr_, rhs.pref_);
			return *this;
		}

		~shared_ptr() {
			Decref();
		}
		void reset() {
			reset_ref(nullptr, nullptr);
		}

		template <class U>
		void reset(U* ptr) {
			shared_ptr<T>(ptr).swap(*this);
		}

		template< class U, class D>
		void reset(U* ptr, D del) {
			shared_ptr<T>(ptr, del).swap(*this);
		}

		T& operator*() const {
			return *(get());
		}
		T* get() const {
			return ptr_;
		}
		T* operator->() const {
			return get();
		}

		void swap(shared_ptr& x) {
			std::swap(ptr_, x.ptr_);
			std::swap(pref_, x.pref_);
		}
		long use_count() const {
			if (!pref_) {
				return 0;
			}
			return pref_->UseCount();
		}
		bool unique() const {
			return use_count() == 1;
		}
		explicit operator bool() const {
			return get() != nullptr;
		}
		template <class U> bool owner_before(shared_ptr<U>& rhs) {
			return pref_ < rhs.pref_;
		}
	private:
        // reset without incref
        void reset_ref_0(element_type* ptr, RefCountBase* refCount) {
			if (pref_) {
				pref_->Decref();
			}
			ptr_ = ptr;
			pref_ = refCount;

        }
		void reset_ref(element_type* ptr, RefCountBase* refCount) {
			if (refCount) {
				refCount->Incref();
			}
            reset_ref_0(ptr, refCount);
		}


		void Decref() {
			if (pref_) {
				pref_->Decref();
				pref_ = nullptr;
			}
		}

        // friends
		template <class U> friend class shared_ptr;
        template <class U, class... Types> friend shared_ptr<U> make_shared(Types&&... args);
	};

    template <class T>
    void swap(shared_ptr<T>& lhs, shared_ptr<T>& rhs) {
        lhs.swap(rhs);
    }

    template < class T, class U >
    bool operator==(const shared_ptr<T>& lhs, const shared_ptr<U>& rhs) {
        return lhs.get() == rhs.get();
    }

    template< class T, class U >
    bool operator!=(const shared_ptr<T>& lhs, const shared_ptr<U>& rhs) {
        return lhs.get() != rhs.get();
    }

    template< class T, class U >
    bool operator<(const shared_ptr<T>& lhs, const shared_ptr<U>& rhs) {
        return lhs.get() < rhs.get();
    }
    template< class T, class U >
    bool operator>(const shared_ptr<T>& lhs, const shared_ptr<U>& rhs) {
        return lhs.get() > rhs.get();
    }
    template< class T, class U >
    bool operator<=(const shared_ptr<T>& lhs, const shared_ptr<U>& rhs) {
        return lhs.get() <= rhs.get();
    }

    template< class T, class U >
    bool operator>=(const shared_ptr<T>& lhs, const shared_ptr<U>& rhs) {
        return lhs.get() >= rhs.get();
    }

    template< class T >
    bool operator==(const shared_ptr<T>& lhs, std::nullptr_t) {
        return lhs.get() == nullptr;
    }

    template< class T >
    bool operator==(std::nullptr_t, const shared_ptr<T>& rhs) {
        return nullptr == rhs.get();
    }

    template< class T >
    bool operator!=(const shared_ptr<T>& lhs, std::nullptr_t) {
        return lhs.get() != nullptr;
    }

    template< class T >
    bool operator!=(std::nullptr_t, const shared_ptr<T>& rhs) {
        return nullptr != rhs.get();
    }

    template< class T >
    bool operator<(const shared_ptr<T>& lhs, std::nullptr_t) {
        return lhs.get() < nullptr;
    }

    template< class T >
    bool operator<(std::nullptr_t, const shared_ptr<T>& rhs) {
        return nullptr < rhs.get();
    }

    template< class T >
    bool operator<=(const shared_ptr<T>& lhs, std::nullptr_t) {
        return lhs.get() <= nullptr;
    }

    template< class T >
    bool operator<=(std::nullptr_t, const shared_ptr<T>& rhs) {
        return nullptr <= rhs.get();
    }

    template< class T >
    bool operator>(const shared_ptr<T>& lhs, std::nullptr_t) {
        return lhs.get() > nullptr;
    }

    template< class T >
    bool operator>(std::nullptr_t, const shared_ptr<T>& rhs) {
        return nullptr > rhs.get();
    }

    template< class T >
    bool operator>=(const shared_ptr<T>& lhs, std::nullptr_t) {
        return lhs.get() >= nullptr;
    }

    template< class T >
    bool operator>=(std::nullptr_t, const shared_ptr<T>& rhs) {
        return nullptr >= rhs.get();
    }
}
