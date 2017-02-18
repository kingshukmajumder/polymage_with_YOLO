#include <stdio.h>

template <typename T1, typename T2> void data_layout_transform(T1 *out, T2 *in, T1 normal_factor, int in_d1, int in_d2, int in_d3) {
    /*
     * inputs:
     * ======
     * T1 - data type of transformed array (output type)
     * T2 - data type of the array to be transformed (input type)
     * normal_factor - will be used to normalize the output array (e.g 255.0f for char -> float)
     * in_d1 -
     * in_d2 -
     * in_d3 -
     *      dimensions of input array (in_d3 being the fastest varying)
     */
    #pragma omp parallel for schedule(static)
    for(int i = 0; i < in_d1; i++)
        for(int j = 0; j< in_d2; j++)
            for(int k = 0; k < in_d3; k++)
                out[k*(in_d1)*(in_d2) + i*(in_d2) + j] = ((T1) in[i*(in_d2)*(in_d3) + j*(in_d3) + k]) / normal_factor;
    
    return;
}

void data_layout_transform_char_to_float(float *out, unsigned char *in, float normal_factor, int in_d1, int in_d2, int in_d3) {
    /*
     * inputs:
     * ======
     * normal_factor - will be used to normalize the output array (e.g 255.0f for char -> float)
     * in_d1 -
     * in_d2 -
     * in_d3 -
     *      dimensions of input array (in_d3 being the fastest varying)
     */
    #pragma omp parallel for schedule(static)
    for(int i = 0; i < in_d1; i++)
        for(int j = 0; j< in_d2; j++)
            for(int k = 0; k < in_d3; k++)
                out[k*(in_d1)*(in_d2) + i*(in_d2) + j] = ((float) in[i*(in_d2)*(in_d3) + j*(in_d3) + k]) / normal_factor;
    
    return;
}
