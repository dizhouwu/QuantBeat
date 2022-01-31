#include <cstdio>
#include <iostream>
#include <exception>

class BadFile: virtual public std::exception
{
public:
    explicit BadFile(const std::string& msg):
            m_msg(msg)
    {}

    virtual ~BadFile() throw () {}

    virtual const char* what() const throw ()
    {
        return m_msg.c_str();
    }

private:
    std::string m_msg;
};

class FileHandlerRAII
{
public:
    FileHandlerRAII(const char* fileName) : m_fp(std::fopen(fileName, "w+"))
    {
        if (m_fp == NULL) {
            throw BadFile(std::string(fileName) + " failed to be opened");
        }
        std::cout << "file resource: " << fileName << " acquired\n";
    }

    FileHandlerRAII(const FileHandlerRAII&)=delete; // no copy operations
    FileHandlerRAII& operator=(const FileHandlerRAII&)=delete;

    FileHandlerRAII(FileHandlerRAII&&)=delete; // no move operations
    FileHandlerRAII& operator=(FileHandlerRAII&&)=delete;

    bool write(const char* str)
    {
        if( std::fputs(str, m_fp) == EOF ) {
            return false ;
        }
        return true;
    }

    ~FileHandlerRAII()
    {
        if (m_fp != NULL) {
            std::fclose(m_fp) ;
            std::cout << "file resource released\n";
        }
    }
private:
    FILE *m_fp;
};

int main()
{
    try {
        FileHandlerRAII raii("test.log");

        for (auto i = 0; i <3; i++) {
            if (raii.write("Hello RAII")) {
                std::cout << "file accessed successfully\n";
            }

//            if (i == 1) {
//                throw std::runtime_error("Bye bye cruel world !");
//            }
        }
    }
    catch(...) {
        std::cout << "something went wrong \n";
    }

    return 0;
}