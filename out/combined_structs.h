#ifndef __COMBINED_STRUCTS_H
#define __COMBINED_STRUCTS_H

#include <stdint.h>

// Used defines
#define MAX_NAME 50

// examples/basic/example2.h : Person
typedef struct {
  birth_date_t birth_date;
} Person;

// examples/basic/example.h : Employee
typedef struct {
  int64_t id;
  char name[MAX_NAME];
  float salary;
  struct {
    int64_t year;
    int64_t month;
    int32_t day;
    uint32_t long_time;
  } hire_date;
  Person Person;
} Employee;

// examples/basic/example.h : Manager
typedef struct {
  int64_t id;
  char name[50];
  float salary;
  Employee employee;
} Manager;

#endif // __COMBINED_STRUCTS_H
