#ifndef COMBINED_STRUCTS_H
#define COMBINED_STRUCTS_H

#include <stdint.h>

// === Used Defines ===
#define MAX_NAME 50

// === Person ===
typedef struct { birth_date_t birth_date ; } Person;
// === Employee ===
typedef struct { long id ; char name [ MAX_NAME ] ; float salary ; struct { long year ; long month ; long day ; ulong long_time ; } hire_date ; Person Person ; } Employee;
// === Manager ===
typedef struct { long id ; char name [ 50 ] ; float salary ; Employee employee ; } Manager;

#endif // COMBINED_STRUCTS_H
