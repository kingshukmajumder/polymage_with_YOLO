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
extern "C" void pipeline_crp(unsigned int C1, unsigned int Fh1, unsigned int Fh2, unsigned int Fhm1, unsigned int Fhm5, unsigned int Fw1, unsigned int Fw2, unsigned int Fwm1, unsigned int Fwm5, unsigned int K1, unsigned int K2, unsigned int X1, unsigned int Y1, void * input_void_arg, void * weights1_void_arg, void * weights2_void_arg, void * maxpool5_void_arg)
{
  double * weights1;
  weights1 = (double *) (weights1_void_arg);
  double * weights2;
  weights2 = (double *) (weights2_void_arg);
  double * maxpool5;
  maxpool5 = (double *) (maxpool5_void_arg);
  double * input;
  input = (double *) (input_void_arg);
  /* users : ['conv1'] */
  double * _arr_4_0;
  _arr_4_0 = (double *) (pool_allocate((sizeof(double) * ((((1 - Fw1) + X1) * ((1 + Y1) - Fh1)) * K1))));
  for (int _i3 = 0; (_i3 <= (X1 - Fw1)); _i3 = (_i3 + 1))
  {
    for (int _i4 = 0; (_i4 <= (-(Fh1) + Y1)); _i4 = (_i4 + 1))
    {
      for (int _i5 = 0; (_i5 < K1); _i5 = (_i5 + 1))
      {
        _arr_4_0[(((_i3 * (((1 + Y1) - Fh1) * K1)) + (_i4 * K1)) + _i5)] = 0;
      }
    }
  }
  for (int _i0 = 0; (_i0 < K1); _i0 = (_i0 + 1))
  {
    for (int _i1 = 0; (_i1 < C1); _i1 = (_i1 + 1))
    {
      for (int _i2 = 0; (_i2 <= (-(Fh1) + Y1)); _i2 = (_i2 + 1))
      {
        for (int _i3 = 0; (_i3 <= (X1 - Fw1)); _i3 = (_i3 + 1))
        {
          for (int _i4 = 0; (_i4 < Fh1); _i4 = (_i4 + 1))
          {
            for (int _i5 = 0; (_i5 < Fw1); _i5 = (_i5 + 1))
            {
              _arr_4_0[(((_i3 * (((1 + Y1) - Fh1) * K1)) + (_i2 * K1)) + _i0)] = (_arr_4_0[(((_i3 * (((1 + Y1) - Fh1) * K1)) + (_i2 * K1)) + _i0)] + (input[((((_i3 + _i5) * (Y1 * C1)) + ((_i2 + _i4) * C1)) + _i1)] * weights1[((((_i5 * ((Fh1 * C1) * K1)) + (_i4 * (C1 * K1))) + (_i1 * K1)) + _i0)]));
            }
          }
        }
      }
    }
  }
  /* users : ['relu1'] */
  double * _arr_4_1;
  _arr_4_1 = (double *) (pool_allocate((sizeof(double) * ((((1 - Fw1) + X1) * ((1 + Y1) - Fh1)) * K1))));
  for (int _i0 = 0; (_i0 <= (X1 - Fw1)); _i0 = (_i0 + 1))
  {
    for (int _i1 = 0; (_i1 <= (-(Fh1) + Y1)); _i1 = (_i1 + 1))
    {
      for (int _i2 = 0; (_i2 < K1); _i2 = (_i2 + 1))
      {
        double _ct0 = (double) (0.0);
        double _ct1 = _arr_4_0[(((_i0 * (((1 + Y1) - Fh1) * K1)) + (_i1 * K1)) + _i2)];
        double _ct2 = (((double) (0.0) > _arr_4_0[(((_i0 * (((1 + Y1) - Fh1) * K1)) + (_i1 * K1)) + _i2)])? _ct0: _ct1);
        _arr_4_1[(((_i0 * (((1 + Y1) - Fh1) * K1)) + (_i1 * K1)) + _i2)] = _ct2;
      }
    }
  }
  pool_deallocate(_arr_4_0);
  /* users : ['maxpool1'] */
  double * _arr_6_2;
  _arr_6_2 = (double *) (pool_allocate((sizeof(double) * (((((((-1 * Fw1) / 2) + (X1 / 2)) + ((-1 * Fwm1) / 2)) + 5) * (((((-1 * Fhm1) / 2) + (Y1 / 2)) + ((-1 * Fh1) / 2)) + 5)) * K1))));
  for (int _i2 = 0; (_i2 <= ((-(Fwm1) - Fw1) + isl_floord((((X1 + Fwm1) + Fw1) + 1), 2))); _i2 = (_i2 + 1))
  {
    for (int _i3 = 0; (_i3 <= ((-(Fh1) - Fhm1) + isl_floord((((Fh1 + Fhm1) + Y1) + 1), 2))); _i3 = (_i3 + 1))
    {
      for (int _i4 = 0; (_i4 < K1); _i4 = (_i4 + 1))
      {
        _arr_6_2[(((_i2 * ((((((-1 * Fhm1) / 2) + (Y1 / 2)) + ((-1 * Fh1) / 2)) + 5) * K1)) + (_i3 * K1)) + _i4)] = 0;
      }
    }
  }
  for (int _i0 = 0; (_i0 < K1); _i0 = (_i0 + 1))
  {
    for (int _i1 = 0; (_i1 <= ((-(Fh1) - Fhm1) + isl_floord((((Fh1 + Fhm1) + Y1) + 1), 2))); _i1 = (_i1 + 1))
    {
      for (int _i2 = 0; (_i2 <= ((-(Fwm1) - Fw1) + isl_floord((((X1 + Fwm1) + Fw1) + 1), 2))); _i2 = (_i2 + 1))
      {
        for (int _i3 = 0; (_i3 < Fhm1); _i3 = (_i3 + 1))
        {
          for (int _i4 = 0; (_i4 < Fwm1); _i4 = (_i4 + 1))
          {
            _arr_6_2[(((_i2 * ((((((-1 * Fhm1) / 2) + (Y1 / 2)) + ((-1 * Fh1) / 2)) + 5) * K1)) + (_i1 * K1)) + _i0)] = ((_arr_6_2[(((_i2 * ((((((-1 * Fhm1) / 2) + (Y1 / 2)) + ((-1 * Fh1) / 2)) + 5) * K1)) + (_i1 * K1)) + _i0)] > _arr_4_1[((((_i4 + (2 * _i2)) * (((1 + Y1) - Fh1) * K1)) + (((2 * _i1) + _i3) * K1)) + _i0)])? _arr_6_2[(((_i2 * ((((((-1 * Fhm1) / 2) + (Y1 / 2)) + ((-1 * Fh1) / 2)) + 5) * K1)) + (_i1 * K1)) + _i0)]: _arr_4_1[((((_i4 + (2 * _i2)) * (((1 + Y1) - Fh1) * K1)) + (((2 * _i1) + _i3) * K1)) + _i0)]);
          }
        }
      }
    }
  }
  pool_deallocate(_arr_4_1);
  /* users : ['conv2_pad'] */
  double * _arr_6_3;
  _arr_6_3 = (double *) (pool_allocate((sizeof(double) * (((((((-1 * Fw1) / 2) + (X1 / 2)) + ((-1 * Fwm1) / 2)) + 5) * (((((-1 * Fhm1) / 2) + (Y1 / 2)) + ((-1 * Fh1) / 2)) + 5)) * K1))));
  for (int _i0 = 2; (_i0 <= (((-(Fwm1) - Fw1) + isl_floord(((X1 + Fwm1) + Fw1), 2)) + 2)); _i0 = (_i0 + 1))
  {
    for (int _i1 = 2; (_i1 <= (((-(Fh1) - Fhm1) + isl_floord(((Fh1 + Fhm1) + Y1), 2)) + 2)); _i1 = (_i1 + 1))
    {
      for (int _i2 = 0; (_i2 < K1); _i2 = (_i2 + 1))
      {
        _arr_6_3[(((_i0 * ((((((-1 * Fhm1) / 2) + (Y1 / 2)) + ((-1 * Fh1) / 2)) + 5) * K1)) + (_i1 * K1)) + _i2)] = _arr_6_2[((((-2 + _i0) * ((((((-1 * Fhm1) / 2) + (Y1 / 2)) + ((-1 * Fh1) / 2)) + 5) * K1)) + ((-2 + _i1) * K1)) + _i2)];
      }
    }
  }
  pool_deallocate(_arr_6_2);
  /* users : ['conv2'] */
  double * _arr_5_4;
  _arr_5_4 = (double *) (pool_allocate((sizeof(double) * ((((((((-1 * Fw1) / 2) + (X1 / 2)) + ((-1 * Fwm1) / 2)) + (-1 * Fw2)) + 6) * ((((((-1 * Fhm1) / 2) + (-1 * Fh2)) + (Y1 / 2)) + ((-1 * Fh1) / 2)) + 6)) * K2))));
  for (int _i3 = 0; (_i3 <= ((((-(Fwm1) - Fw1) - Fw2) + isl_floord((((X1 + Fwm1) + Fw1) + 1), 2)) + 5)); _i3 = (_i3 + 1))
  {
    for (int _i4 = 0; (_i4 <= ((((-(Fh1) - Fhm1) - Fh2) + isl_floord((((Fh1 + Fhm1) + Y1) + 1), 2)) + 5)); _i4 = (_i4 + 1))
    {
      for (int _i5 = 0; (_i5 < K2); _i5 = (_i5 + 1))
      {
        _arr_5_4[(((_i3 * (((((((-1 * Fhm1) / 2) + (-1 * Fh2)) + (Y1 / 2)) + ((-1 * Fh1) / 2)) + 6) * K2)) + (_i4 * K2)) + _i5)] = 0;
      }
    }
  }
  for (int _i0 = 0; (_i0 < K2); _i0 = (_i0 + 1))
  {
    for (int _i1 = 0; (_i1 < K1); _i1 = (_i1 + 1))
    {
      for (int _i2 = 0; (_i2 <= ((((-(Fh1) - Fhm1) - Fh2) + isl_floord((((Fh1 + Fhm1) + Y1) + 1), 2)) + 5)); _i2 = (_i2 + 1))
      {
        for (int _i3 = 0; (_i3 <= ((((-(Fwm1) - Fw1) - Fw2) + isl_floord((((X1 + Fwm1) + Fw1) + 1), 2)) + 5)); _i3 = (_i3 + 1))
        {
          for (int _i4 = 0; (_i4 < Fh2); _i4 = (_i4 + 1))
          {
            for (int _i5 = 0; (_i5 < Fw2); _i5 = (_i5 + 1))
            {
              _arr_5_4[(((_i3 * (((((((-1 * Fhm1) / 2) + (-1 * Fh2)) + (Y1 / 2)) + ((-1 * Fh1) / 2)) + 6) * K2)) + (_i2 * K2)) + _i0)] = (_arr_5_4[(((_i3 * (((((((-1 * Fhm1) / 2) + (-1 * Fh2)) + (Y1 / 2)) + ((-1 * Fh1) / 2)) + 6) * K2)) + (_i2 * K2)) + _i0)] + (_arr_6_3[((((_i3 + _i5) * ((((((-1 * Fhm1) / 2) + (Y1 / 2)) + ((-1 * Fh1) / 2)) + 5) * K1)) + ((_i4 + _i2) * K1)) + _i1)] * weights2[((((_i5 * ((Fh2 * K1) * K2)) + (_i4 * (K1 * K2))) + (_i1 * K2)) + _i0)]));
            }
          }
        }
      }
    }
  }
  pool_deallocate(_arr_6_3);
  /* users : ['relu4'] */
  double * _arr_5_5;
  _arr_5_5 = (double *) (pool_allocate((sizeof(double) * ((((((((-1 * Fw1) / 2) + (X1 / 2)) + ((-1 * Fwm1) / 2)) + (-1 * Fw2)) + 6) * ((((((-1 * Fhm1) / 2) + (-1 * Fh2)) + (Y1 / 2)) + ((-1 * Fh1) / 2)) + 6)) * K2))));
  for (int _i0 = 0; (_i0 <= ((((-(Fwm1) - Fw1) - Fw2) + isl_floord((((X1 + Fwm1) + Fw1) + 1), 2)) + 1)); _i0 = (_i0 + 1))
  {
    for (int _i1 = 0; (_i1 <= ((((-(Fh1) - Fhm1) - Fh2) + isl_floord((((Fh1 + Fhm1) + Y1) + 1), 2)) + 1)); _i1 = (_i1 + 1))
    {
      for (int _i2 = 0; (_i2 < K2); _i2 = (_i2 + 1))
      {
        double _ct3 = (double) (0.0);
        double _ct4 = _arr_5_4[(((_i0 * (((((((-1 * Fhm1) / 2) + (-1 * Fh2)) + (Y1 / 2)) + ((-1 * Fh1) / 2)) + 6) * K2)) + (_i1 * K2)) + _i2)];
        double _ct5 = (((double) (0.0) > _arr_5_4[(((_i0 * (((((((-1 * Fhm1) / 2) + (-1 * Fh2)) + (Y1 / 2)) + ((-1 * Fh1) / 2)) + 6) * K2)) + (_i1 * K2)) + _i2)])? _ct3: _ct4);
        _arr_5_5[(((_i0 * (((((((-1 * Fhm1) / 2) + (-1 * Fh2)) + (Y1 / 2)) + ((-1 * Fh1) / 2)) + 6) * K2)) + (_i1 * K2)) + _i2)] = _ct5;
      }
    }
  }
  pool_deallocate(_arr_5_4);
  for (int _i2 = 0; (_i2 <= (((-(Fwm5) - Fw2) + isl_floord((((((X1 - Fwm1) - Fw1) + (2 * Fwm5)) + (2 * Fw2)) + 1), 4)) + 1)); _i2 = (_i2 + 1))
  {
    for (int _i3 = 0; (_i3 <= (((-(Fh2) - Fhm5) + isl_floord((((((-(Fh1) - Fhm1) + (2 * Fh2)) + Y1) + (2 * Fhm5)) + 1), 4)) + 1)); _i3 = (_i3 + 1))
    {
      for (int _i4 = 0; (_i4 < K2); _i4 = (_i4 + 1))
      {
        maxpool5[(((_i2 * ((((((((-1 * Fh1) / 4) + ((-1 * Fhm1) / 4)) + ((-1 * Fh2) / 2)) + (Y1 / 4)) + ((-1 * Fhm5) / 2)) + 2) * K2)) + (_i3 * K2)) + _i4)] = 0;
      }
    }
  }
  for (int _i0 = 0; (_i0 < K2); _i0 = (_i0 + 1))
  {
    for (int _i1 = 0; (_i1 <= (((-(Fh2) - Fhm5) + isl_floord((((((-(Fh1) - Fhm1) + (2 * Fh2)) + Y1) + (2 * Fhm5)) + 1), 4)) + 1)); _i1 = (_i1 + 1))
    {
      for (int _i2 = 0; (_i2 <= (((-(Fwm5) - Fw2) + isl_floord((((((X1 - Fwm1) - Fw1) + (2 * Fwm5)) + (2 * Fw2)) + 1), 4)) + 1)); _i2 = (_i2 + 1))
      {
        for (int _i3 = 0; (_i3 < Fhm5); _i3 = (_i3 + 1))
        {
          for (int _i4 = 0; (_i4 < Fwm5); _i4 = (_i4 + 1))
          {
            maxpool5[(((_i2 * ((((((((-1 * Fh1) / 4) + ((-1 * Fhm1) / 4)) + ((-1 * Fh2) / 2)) + (Y1 / 4)) + ((-1 * Fhm5) / 2)) + 2) * K2)) + (_i1 * K2)) + _i0)] = ((maxpool5[(((_i2 * ((((((((-1 * Fh1) / 4) + ((-1 * Fhm1) / 4)) + ((-1 * Fh2) / 2)) + (Y1 / 4)) + ((-1 * Fhm5) / 2)) + 2) * K2)) + (_i1 * K2)) + _i0)] > _arr_5_5[((((_i4 + (2 * _i2)) * (((((((-1 * Fhm1) / 2) + (-1 * Fh2)) + (Y1 / 2)) + ((-1 * Fh1) / 2)) + 6) * K2)) + (((2 * _i1) + _i3) * K2)) + _i0)])? maxpool5[(((_i2 * ((((((((-1 * Fh1) / 4) + ((-1 * Fhm1) / 4)) + ((-1 * Fh2) / 2)) + (Y1 / 4)) + ((-1 * Fhm5) / 2)) + 2) * K2)) + (_i1 * K2)) + _i0)]: _arr_5_5[((((_i4 + (2 * _i2)) * (((((((-1 * Fhm1) / 2) + (-1 * Fh2)) + (Y1 / 2)) + ((-1 * Fh1) / 2)) + 6) * K2)) + (((2 * _i1) + _i3) * K2)) + _i0)]);
          }
        }
      }
    }
  }
  pool_deallocate(_arr_5_5);
}