#include "dsp_helpers.h"

double chbevl(double x, int arr_typ) {
    double *array;
    int n;
    if (!arr_typ) {
        array = A;
        n = 30;
    } else {
        array = B;
        n = 25;
    }

    double b0, b1, b2, *p;
    int i;

    p = array;
    b0 = *p++;
    b1 = 0.0;
    i = n - 1;

    do {
        b2 = b1;
        b1 = b0;
        b0 = x * b1 - b2 + *p++;
	} while (--i);

    return 0.5 * (b0 - b2);
}
