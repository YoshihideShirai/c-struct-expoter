// example.h

typedef unsigned int ulong:

#include "example2.h"

typedef struct {
    long id;
    char name[MAX_NAME];
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
