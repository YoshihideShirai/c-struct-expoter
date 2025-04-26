// example.h

typedef unsigned int ulong:

typedef struct {
    long year;
    long month;
    long day;
} birth_date_t;

typedef struct {
    birth_date_t birth_date;
} Person;

typedef struct {
    long id;
    char name[50];
    float salary;
    struct {
        long year;
        long month;
        long day;
        ulong long_time;
    } hire_date;
    Person Person;
} Employee;

typedef struct {
    long id;
    char name[50];
    float salary;
    Employee employee;
} Manager
