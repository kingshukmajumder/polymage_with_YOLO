#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include "dsp_helpers.h"

int main(int argc, char **argv) {
    double values[] = {0.0, 1e-10, 0.1, 0.5, 1.0, 2.5, 5.0, 20.0};
    double expected_results[] = {1.0, 1.0, 0.9071009258, 0.6450352706, \
                0.4657596077, 0.2700464416, 0.1835408126, 0.0897803119};
    int i;
    double x, y, cv, ecv;

    for (i = 0; i < 8; i++) {
        x = values[i];
        if (x <= 8.0) {
            y = x / 2.0 - 2.0;
            cv = chbevl(y, 0);
        } else {
            cv = chbevl(32.0 / x - 2.0, 1) / sqrt(x);
        }

        ecv = expected_results[i];
        if (fabs(cv - ecv) >= 1e-8) {
            printf("Error in evaluation for test %d\n", i);
            printf("value = %lf\n", x);
            printf("computed result = %lf\n", cv);
            printf("expected result = %lf\n", ecv);
            exit(1);
        }
    }

    printf("All tests passed!\n");
    return 0;
}
