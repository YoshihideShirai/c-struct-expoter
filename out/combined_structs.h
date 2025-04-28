#ifndef EXTRACTED_STRUCTS_H
#define EXTRACTED_STRUCTS_H

#include <stdint.h>

// Used defines
#define MAX_NAME 50

// examples/basic/example2.h : Person
typedef struct { birth_date_t birth_date ; } Person;

// examples/basic/example.h : Employee
typedef struct { int64_t id ; char name [ MAX_NAME ] ; float salary ; struct { int64_t year ; int64_t month ; int64_t day ; ulong long_time ; } hire_date ; Person Person ; } Employee;

// examples/basic/example.h : Manager
typedef struct { int64_t id ; char name [ 50 ] ; float salary ; Employee employee ; } Manager;

#endif // EXTRACTED_STRUCTS_H
