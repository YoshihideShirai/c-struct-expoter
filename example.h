// example.h
typedef struct {
    long year;
    long month;
    long day;
} birth_date_t;

typedef struct {
    long id;
    char name[50];
    float salary;
    struct {
        long year;
        long month;
        long day;
        long long_time;
    } hire_date;
    birth_date_t birth_date;
} Employee;
