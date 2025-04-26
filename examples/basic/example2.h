
#define MAX_NAME 50
#define BONUS_RATE 0.1

typedef struct {
    long year;
    long month;
    long day;
} birth_date_t;

typedef struct {
    birth_date_t birth_date;
} Person;
