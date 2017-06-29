#include <stdio.h>
#include <stdlib.h>
#include <malloc.h>
#include <cmath>
#include <complex>
#include <string.h>
#include <simple_pool_allocator.h>
#define isl_min(x,y) ((x) < (y) ? (x) : (y))
#define isl_max(x,y) ((x) > (y) ? (x) : (y))
#define isl_floord(n,d) (((n)<0) ? -((-(n)+(d)-1)/(d)) : (n)/(d))
extern "C" void pipeline_matvec(int C, int R, void * mat1_void_arg, void * v1_void_arg, void * v2_void_arg, void * v3_void_arg, void * _mul_00_void_arg, void * _mul_59_void_arg, void * _mul_86_void_arg)
{
  double * v2;
  v2 = (double *) (v2_void_arg);
  double * mat1;
  mat1 = (double *) (mat1_void_arg);
  double * _mul_59;
  _mul_59 = (double *) (_mul_59_void_arg);
  double * v3;
  v3 = (double *) (v3_void_arg);
  double * v1;
  v1 = (double *) (v1_void_arg);
  double * _mul_00;
  _mul_00 = (double *) (_mul_00_void_arg);
  double * _mul_86;
  _mul_86 = (double *) (_mul_86_void_arg);
  for (int _i1 = 0; (_i1 <= 127); _i1 = (_i1 + 1))
  {
    _mul_59[_i1] = 0;
  }
  for (int _i0 = 0; (_i0 <= 127); _i0 = (_i0 + 1))
  {
    for (int _i2 = 0; (_i2 <= 127); _i2 = (_i2 + 1))
    {
      if ((C == C))
      {
        _mul_59[_i0] = (_mul_59[_i0] + (mat1[((_i0 * C) + _i2)] * v1[_i2]));
      }
    }
  }
  for (int _i1 = 0; (_i1 <= 127); _i1 = (_i1 + 1))
  {
    _mul_00[_i1] = 0;
  }
  for (int _i0 = 0; (_i0 <= 127); _i0 = (_i0 + 1))
  {
    for (int _i2 = 0; (_i2 <= 127); _i2 = (_i2 + 1))
    {
      if ((C == C))
      {
        _mul_00[_i0] = (_mul_00[_i0] + (mat1[((_i0 * C) + _i2)] * v3[_i2]));
      }
    }
  }
  for (int _i1 = 0; (_i1 <= 127); _i1 = (_i1 + 1))
  {
    _mul_86[_i1] = 0;
  }
  for (int _i0 = 0; (_i0 <= 127); _i0 = (_i0 + 1))
  {
    for (int _i2 = 0; (_i2 <= 127); _i2 = (_i2 + 1))
    {
      if ((C == C))
      {
        _mul_86[_i0] = (_mul_86[_i0] + (mat1[((_i0 * C) + _i2)] * v2[_i2]));
      }
    }
  }
}