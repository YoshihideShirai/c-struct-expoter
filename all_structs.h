#ifndef COMBINED_STRUCTS_H
#define COMBINED_STRUCTS_H

#include <stdint.h>

// === Used Defines ===
#define MAX_NAME 50

// === Person ===
    struct {
        long year;
        long month;

// === Employee ===
typedef struct {
    int64_t id;
    char name[MAX_NAME];
    float salary;
    struct {
        int64_t year;
        int64_t month;
        int64_t day;
        uint32_t long_time;
    } hire_date;
    Person Person;
} Employee;

// === Manager ===
typedef struct {
    int64_t id;
    char name[50];
    float salary;
    Employee employee;
} Manager


#endif // COMBINED_STRUCTS_H
