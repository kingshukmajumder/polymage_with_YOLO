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
extern "C" void pipeline_crp(unsigned int C1, unsigned int Fh1, unsigned int Fh2, unsigned int Fh3, unsigned int Fh4, unsigned int Fhm1, unsigned int Fhm2, unsigned int Fw1, unsigned int Fw2, unsigned int Fw3, unsigned int Fw4, unsigned int Fwm1, unsigned int Fwm2, unsigned int K1, unsigned int K2, unsigned int K3, unsigned int K4, unsigned int X1, unsigned int Y1, void * input_void_arg, void * weights1_void_arg, void * weights2_void_arg, void * weights3_void_arg, void * weights4_void_arg, void * maxpool2_void_arg)
{
  double * maxpool2;
  maxpool2 = (double *) (maxpool2_void_arg);
  double * weights3;
  weights3 = (double *) (weights3_void_arg);
  double * input;
  input = (double *) (input_void_arg);
  double * weights1;
  weights1 = (double *) (weights1_void_arg);
  double * weights2;
  weights2 = (double *) (weights2_void_arg);
  double * weights4;
  weights4 = (double *) (weights4_void_arg);
  /* users : ['conv1_pad'] */
  double * _arr_15_0;
  _arr_15_0 = (double *) (pool_allocate((sizeof(double) * (((2 + X1) * (2 + Y1)) * C1))));
  for (int _i0 = 1; (_i0 <= X1); _i0 = (_i0 + 1))
  {
    for (int _i1 = 1; (_i1 <= Y1); _i1 = (_i1 + 1))
    {
      for (int _i2 = 0; (_i2 < C1); _i2 = (_i2 + 1))
      {
        _arr_15_0[(((_i0 * ((2 + Y1) * C1)) + (_i1 * C1)) + _i2)] = input[((((-1 + _i0) * (Y1 * C1)) + ((-1 + _i1) * C1)) + _i2)];
      }
    }
  }
  /* users : ['conv1'] */
  double * _arr_9_1;
  _arr_9_1 = (double *) (pool_allocate((sizeof(double) * ((((3 + X1) - Fw1) * ((3 - Fh1) + Y1)) * K1))));
  for (int _i3 = 0; (_i3 <= ((-(Fw1) + X1) + 2)); _i3 = (_i3 + 1))
  {
    for (int _i4 = 0; (_i4 <= ((-(Fh1) + Y1) + 2)); _i4 = (_i4 + 1))
    {
      for (int _i5 = 0; (_i5 < K1); _i5 = (_i5 + 1))
      {
        _arr_9_1[(((_i3 * (((3 - Fh1) + Y1) * K1)) + (_i4 * K1)) + _i5)] = 0;
      }
    }
  }
  for (int _i0 = 0; (_i0 < K1); _i0 = (_i0 + 1))
  {
    for (int _i1 = 0; (_i1 < C1); _i1 = (_i1 + 1))
    {
      for (int _i2 = 0; (_i2 <= ((-(Fh1) + Y1) + 2)); _i2 = (_i2 + 1))
      {
        for (int _i3 = 0; (_i3 <= ((-(Fw1) + X1) + 2)); _i3 = (_i3 + 1))
        {
          for (int _i4 = 0; (_i4 < Fh1); _i4 = (_i4 + 1))
          {
            for (int _i5 = 0; (_i5 < Fw1); _i5 = (_i5 + 1))
            {
              _arr_9_1[(((_i3 * (((3 - Fh1) + Y1) * K1)) + (_i2 * K1)) + _i0)] = (_arr_9_1[(((_i3 * (((3 - Fh1) + Y1) * K1)) + (_i2 * K1)) + _i0)] + (_arr_15_0[((((_i3 + _i5) * ((2 + Y1) * C1)) + ((_i4 + _i2) * C1)) + _i1)] * weights1[((((_i5 * ((Fh1 * C1) * K1)) + (_i4 * (C1 * K1))) + (_i1 * K1)) + _i0)]));
            }
          }
        }
      }
    }
  }
  pool_deallocate(_arr_15_0);
  /* users : ['conv2_pad'] */
  double * _arr_9_3;
  _arr_9_3 = (double *) (pool_allocate((sizeof(double) * ((((3 + X1) - Fw1) * ((3 - Fh1) + Y1)) * K1))));
  #pragma omp parallel for schedule(static)
  for (int _T_i0 = -1; (_T_i0 <= ((X1 - Fw1) / 16)); _T_i0 = (_T_i0 + 1))
  {
    /* users : ['relu1'] */
    double _buf_5_2[((17 * 17) * 16)];
    for (int _T_i1 = -1; (_T_i1 <= ((-(Fh1) + Y1) / 16)); _T_i1 = (_T_i1 + 1))
    {
      for (int _T_i2 = 0; (_T_i2 <= ((K1 - 1) / 16)); _T_i2 = (_T_i2 + 1))
      {
        int _ct0 = (((X1 - Fw1) < ((16 * _T_i0) + 16))? (X1 - Fw1): ((16 * _T_i0) + 16));
        int _ct1 = ((0 > (16 * _T_i0))? 0: (16 * _T_i0));
        for (int _i0 = _ct1; (_i0 <= _ct0); _i0 = (_i0 + 1))
        {
          int _ct2 = (((-(Fh1) + Y1) < ((16 * _T_i1) + 16))? (-(Fh1) + Y1): ((16 * _T_i1) + 16));
          int _ct3 = ((0 > (16 * _T_i1))? 0: (16 * _T_i1));
          for (int _i1 = _ct3; (_i1 <= _ct2); _i1 = (_i1 + 1))
          {
            int _ct4 = (((K1 - 1) < ((16 * _T_i2) + 15))? (K1 - 1): ((16 * _T_i2) + 15));
            #pragma ivdep
            for (int _i2 = (16 * _T_i2); (_i2 <= _ct4); _i2 = (_i2 + 1))
            {
              double _ct5 = (double) (0.0);
              double _ct6 = _arr_9_1[(((_i0 * (((3 - Fh1) + Y1) * K1)) + (_i1 * K1)) + _i2)];
              double _ct7 = (((double) (0.0) > _arr_9_1[(((_i0 * (((3 - Fh1) + Y1) * K1)) + (_i1 * K1)) + _i2)])? _ct5: _ct6);
              _buf_5_2[(((((-16 * _T_i0) + _i0) * (17 * 16)) + (((-16 * _T_i1) + _i1) * 16)) + ((-16 * _T_i2) + _i2))] = _ct7;
            }
          }
        }
        if (((_T_i0 >= 0) && (_T_i1 >= 0)))
        {
          int _ct8 = ((((X1 - Fw1) + 1) < ((16 * _T_i0) + 16))? ((X1 - Fw1) + 1): ((16 * _T_i0) + 16));
          for (int _i0 = ((16 * _T_i0) + 1); (_i0 <= _ct8); _i0 = (_i0 + 1))
          {
            int _ct9 = ((((-(Fh1) + Y1) + 1) < ((16 * _T_i1) + 16))? ((-(Fh1) + Y1) + 1): ((16 * _T_i1) + 16));
            for (int _i1 = ((16 * _T_i1) + 1); (_i1 <= _ct9); _i1 = (_i1 + 1))
            {
              int _ct10 = (((K1 - 1) < ((16 * _T_i2) + 15))? (K1 - 1): ((16 * _T_i2) + 15));
              #pragma ivdep
              for (int _i2 = (16 * _T_i2); (_i2 <= _ct10); _i2 = (_i2 + 1))
              {
                _arr_9_3[(((_i0 * (((3 - Fh1) + Y1) * K1)) + (_i1 * K1)) + _i2)] = _buf_5_2[((((-1 + ((-16 * _T_i0) + _i0)) * (17 * 16)) + ((-1 + ((-16 * _T_i1) + _i1)) * 16)) + ((-16 * _T_i2) + _i2))];
              }
            }
          }
        }
      }
    }
  }
  pool_deallocate(_arr_9_1);
  /* users : ['conv2'] */
  double * _arr_14_4;
  _arr_14_4 = (double *) (pool_allocate((sizeof(double) * (((((4 - Fw2) + X1) - Fw1) * (((4 - Fh1) + Y1) - Fh2)) * K2))));
  for (int _i3 = 0; (_i3 <= (((-(Fw1) - Fw2) + X1) + 3)); _i3 = (_i3 + 1))
  {
    for (int _i4 = 0; (_i4 <= (((-(Fh1) - Fh2) + Y1) + 3)); _i4 = (_i4 + 1))
    {
      for (int _i5 = 0; (_i5 < K2); _i5 = (_i5 + 1))
      {
        _arr_14_4[(((_i3 * ((((4 - Fh1) + Y1) - Fh2) * K2)) + (_i4 * K2)) + _i5)] = 0;
      }
    }
  }
  for (int _i0 = 0; (_i0 < K2); _i0 = (_i0 + 1))
  {
    for (int _i1 = 0; (_i1 < K1); _i1 = (_i1 + 1))
    {
      for (int _i2 = 0; (_i2 <= (((-(Fh1) - Fh2) + Y1) + 3)); _i2 = (_i2 + 1))
      {
        for (int _i3 = 0; (_i3 <= (((-(Fw1) - Fw2) + X1) + 3)); _i3 = (_i3 + 1))
        {
          for (int _i4 = 0; (_i4 < Fh2); _i4 = (_i4 + 1))
          {
            for (int _i5 = 0; (_i5 < Fw2); _i5 = (_i5 + 1))
            {
              _arr_14_4[(((_i3 * ((((4 - Fh1) + Y1) - Fh2) * K2)) + (_i2 * K2)) + _i0)] = (_arr_14_4[(((_i3 * ((((4 - Fh1) + Y1) - Fh2) * K2)) + (_i2 * K2)) + _i0)] + (_arr_9_3[((((_i3 + _i5) * (((3 - Fh1) + Y1) * K1)) + ((_i4 + _i2) * K1)) + _i1)] * weights2[((((_i5 * ((Fh2 * K1) * K2)) + (_i4 * (K1 * K2))) + (_i1 * K2)) + _i0)]));
            }
          }
        }
      }
    }
  }
  pool_deallocate(_arr_9_3);
  /* users : ['relu2'] */
  double * _arr_14_5;
  _arr_14_5 = (double *) (pool_allocate((sizeof(double) * (((((4 - Fw2) + X1) - Fw1) * (((4 - Fh1) + Y1) - Fh2)) * K2))));
  for (int _i0 = 0; (_i0 <= (((-(Fw1) - Fw2) + X1) + 1)); _i0 = (_i0 + 1))
  {
    for (int _i1 = 0; (_i1 <= (((-(Fh1) - Fh2) + Y1) + 1)); _i1 = (_i1 + 1))
    {
      for (int _i2 = 0; (_i2 < K2); _i2 = (_i2 + 1))
      {
        double _ct11 = (double) (0.0);
        double _ct12 = _arr_14_4[(((_i0 * ((((4 - Fh1) + Y1) - Fh2) * K2)) + (_i1 * K2)) + _i2)];
        double _ct13 = (((double) (0.0) > _arr_14_4[(((_i0 * ((((4 - Fh1) + Y1) - Fh2) * K2)) + (_i1 * K2)) + _i2)])? _ct11: _ct12);
        _arr_14_5[(((_i0 * ((((4 - Fh1) + Y1) - Fh2) * K2)) + (_i1 * K2)) + _i2)] = _ct13;
      }
    }
  }
  pool_deallocate(_arr_14_4);
  /* users : ['maxpool1'] */
  double * _arr_13_6;
  _arr_13_6 = (double *) (pool_allocate((sizeof(double) * ((((((((-1 * Fw2) / 2) + ((-1 * Fwm1) / 2)) + (X1 / 2)) + ((-1 * Fw1) / 2)) + 2) * ((((((-1 * Fhm1) / 2) + ((-1 * Fh1) / 2)) + (Y1 / 2)) + ((-1 * Fh2) / 2)) + 2)) * K2))));
  for (int _i2 = 0; (_i2 <= ((((-(Fwm1) - Fw1) - Fw2) + isl_floord((((Fwm1 + Fw1) + Fw2) + X1), 2)) + 1)); _i2 = (_i2 + 1))
  {
    for (int _i3 = 0; (_i3 <= ((((-(Fh1) - Fh2) - Fhm1) + isl_floord((((Fh1 + Fh2) + Fhm1) + Y1), 2)) + 1)); _i3 = (_i3 + 1))
    {
      for (int _i4 = 0; (_i4 < K2); _i4 = (_i4 + 1))
      {
        _arr_13_6[(((_i2 * (((((((-1 * Fhm1) / 2) + ((-1 * Fh1) / 2)) + (Y1 / 2)) + ((-1 * Fh2) / 2)) + 2) * K2)) + (_i3 * K2)) + _i4)] = 0;
      }
    }
  }
  for (int _i0 = 0; (_i0 < K2); _i0 = (_i0 + 1))
  {
    for (int _i1 = 0; (_i1 <= ((((-(Fh1) - Fh2) - Fhm1) + isl_floord((((Fh1 + Fh2) + Fhm1) + Y1), 2)) + 1)); _i1 = (_i1 + 1))
    {
      for (int _i2 = 0; (_i2 <= ((((-(Fwm1) - Fw1) - Fw2) + isl_floord((((Fwm1 + Fw1) + Fw2) + X1), 2)) + 1)); _i2 = (_i2 + 1))
      {
        for (int _i3 = 0; (_i3 < Fhm1); _i3 = (_i3 + 1))
        {
          for (int _i4 = 0; (_i4 < Fwm1); _i4 = (_i4 + 1))
          {
            _arr_13_6[(((_i2 * (((((((-1 * Fhm1) / 2) + ((-1 * Fh1) / 2)) + (Y1 / 2)) + ((-1 * Fh2) / 2)) + 2) * K2)) + (_i1 * K2)) + _i0)] = ((_arr_13_6[(((_i2 * (((((((-1 * Fhm1) / 2) + ((-1 * Fh1) / 2)) + (Y1 / 2)) + ((-1 * Fh2) / 2)) + 2) * K2)) + (_i1 * K2)) + _i0)] > _arr_14_5[(((((2 * _i2) + _i4) * ((((4 - Fh1) + Y1) - Fh2) * K2)) + ((_i3 + (2 * _i1)) * K2)) + _i0)])? _arr_13_6[(((_i2 * (((((((-1 * Fhm1) / 2) + ((-1 * Fh1) / 2)) + (Y1 / 2)) + ((-1 * Fh2) / 2)) + 2) * K2)) + (_i1 * K2)) + _i0)]: _arr_14_5[(((((2 * _i2) + _i4) * ((((4 - Fh1) + Y1) - Fh2) * K2)) + ((_i3 + (2 * _i1)) * K2)) + _i0)]);
          }
        }
      }
    }
  }
  pool_deallocate(_arr_14_5);
  /* users : ['conv3_pad'] */
  double * _arr_8_7;
  _arr_8_7 = (double *) (pool_allocate((sizeof(double) * ((((((((-1 * Fw2) / 2) + ((-1 * Fw1) / 2)) + (X1 / 2)) + ((-1 * Fwm1) / 2)) + 4) * ((((((-1 * Fhm1) / 2) + ((-1 * Fh1) / 2)) + (Y1 / 2)) + ((-1 * Fh2) / 2)) + 4)) * K2))));
  for (int _i0 = 1; (_i0 <= ((((-(Fwm1) - Fw1) - Fw2) + isl_floord(((((Fwm1 + Fw1) + Fw2) + X1) + 1), 2)) + 1)); _i0 = (_i0 + 1))
  {
    for (int _i1 = 1; (_i1 <= ((((-(Fh1) - Fh2) - Fhm1) + isl_floord(((((Fh1 + Fh2) + Fhm1) + Y1) + 1), 2)) + 1)); _i1 = (_i1 + 1))
    {
      for (int _i2 = 0; (_i2 < K2); _i2 = (_i2 + 1))
      {
        _arr_8_7[(((_i0 * (((((((-1 * Fhm1) / 2) + ((-1 * Fh1) / 2)) + (Y1 / 2)) + ((-1 * Fh2) / 2)) + 4) * K2)) + (_i1 * K2)) + _i2)] = _arr_13_6[((((-1 + _i0) * (((((((-1 * Fhm1) / 2) + ((-1 * Fh1) / 2)) + (Y1 / 2)) + ((-1 * Fh2) / 2)) + 2) * K2)) + ((-1 + _i1) * K2)) + _i2)];
      }
    }
  }
  pool_deallocate(_arr_13_6);
  /* users : ['conv3'] */
  double * _arr_11_8;
  _arr_11_8 = (double *) (pool_allocate((sizeof(double) * ((((((((-1 * Fw3) + ((-1 * Fw2) / 2)) + ((-1 * Fw1) / 2)) + (X1 / 2)) + ((-1 * Fwm1) / 2)) + 5) * (((((((-1 * Fhm1) / 2) + ((-1 * Fh1) / 2)) + (Y1 / 2)) + (-1 * Fh3)) + ((-1 * Fh2) / 2)) + 5)) * K3))));
  for (int _i3 = 0; (_i3 <= (((((-(Fw1) - Fwm1) - Fw2) - Fw3) + isl_floord((((Fw1 + Fwm1) + Fw2) + X1), 2)) + 4)); _i3 = (_i3 + 1))
  {
    for (int _i4 = 0; (_i4 <= (((((-(Fh1) - Fh2) - Fhm1) - Fh3) + isl_floord((((Fh1 + Fh2) + Fhm1) + Y1), 2)) + 4)); _i4 = (_i4 + 1))
    {
      for (int _i5 = 0; (_i5 < K3); _i5 = (_i5 + 1))
      {
        _arr_11_8[(((_i3 * ((((((((-1 * Fhm1) / 2) + ((-1 * Fh1) / 2)) + (Y1 / 2)) + (-1 * Fh3)) + ((-1 * Fh2) / 2)) + 5) * K3)) + (_i4 * K3)) + _i5)] = 0;
      }
    }
  }
  for (int _i0 = 0; (_i0 < K3); _i0 = (_i0 + 1))
  {
    for (int _i1 = 0; (_i1 < K2); _i1 = (_i1 + 1))
    {
      for (int _i2 = 0; (_i2 <= (((((-(Fh1) - Fh2) - Fhm1) - Fh3) + isl_floord((((Fh1 + Fh2) + Fhm1) + Y1), 2)) + 4)); _i2 = (_i2 + 1))
      {
        for (int _i3 = 0; (_i3 <= (((((-(Fw1) - Fwm1) - Fw2) - Fw3) + isl_floord((((Fw1 + Fwm1) + Fw2) + X1), 2)) + 4)); _i3 = (_i3 + 1))
        {
          for (int _i4 = 0; (_i4 < Fh3); _i4 = (_i4 + 1))
          {
            for (int _i5 = 0; (_i5 < Fw3); _i5 = (_i5 + 1))
            {
              _arr_11_8[(((_i3 * ((((((((-1 * Fhm1) / 2) + ((-1 * Fh1) / 2)) + (Y1 / 2)) + (-1 * Fh3)) + ((-1 * Fh2) / 2)) + 5) * K3)) + (_i2 * K3)) + _i0)] = (_arr_11_8[(((_i3 * ((((((((-1 * Fhm1) / 2) + ((-1 * Fh1) / 2)) + (Y1 / 2)) + (-1 * Fh3)) + ((-1 * Fh2) / 2)) + 5) * K3)) + (_i2 * K3)) + _i0)] + (_arr_8_7[((((_i3 + _i5) * (((((((-1 * Fhm1) / 2) + ((-1 * Fh1) / 2)) + (Y1 / 2)) + ((-1 * Fh2) / 2)) + 4) * K2)) + ((_i2 + _i4) * K2)) + _i1)] * weights3[((((_i5 * ((Fh3 * K2) * K3)) + (_i4 * (K2 * K3))) + (_i1 * K3)) + _i0)]));
            }
          }
        }
      }
    }
  }
  pool_deallocate(_arr_8_7);
  /* users : ['conv4_pad'] */
  double * _arr_11_10;
  _arr_11_10 = (double *) (pool_allocate((sizeof(double) * ((((((((-1 * Fw3) + ((-1 * Fw2) / 2)) + ((-1 * Fw1) / 2)) + (X1 / 2)) + ((-1 * Fwm1) / 2)) + 5) * (((((((-1 * Fhm1) / 2) + ((-1 * Fh1) / 2)) + (Y1 / 2)) + (-1 * Fh3)) + ((-1 * Fh2) / 2)) + 5)) * K3))));
  #pragma omp parallel for schedule(static)
  for (int _T_i0 = -1; (_T_i0 <= ((((((-(Fwm1) - Fw1) - Fw2) + X1) - (2 * Fw3)) + 4) / 32)); _T_i0 = (_T_i0 + 1))
  {
    /* users : ['relu3'] */
    double _buf_6_9[((17 * 17) * 16)];
    for (int _T_i1 = -1; (_T_i1 <= ((((((-(Fh1) - Fh2) - Fhm1) - (2 * Fh3)) + Y1) + 4) / 32)); _T_i1 = (_T_i1 + 1))
    {
      for (int _T_i2 = 0; (_T_i2 <= ((K3 - 1) / 16)); _T_i2 = (_T_i2 + 1))
      {
        int _ct14 = ((((16 * _T_i0) + 16) < (((((-(Fwm1) - Fw1) - Fw2) - Fw3) + isl_floord((((Fwm1 + Fw1) + Fw2) + X1), 2)) + 2))? ((16 * _T_i0) + 16): (((((-(Fwm1) - Fw1) - Fw2) - Fw3) + isl_floord((((Fwm1 + Fw1) + Fw2) + X1), 2)) + 2));
        int _ct15 = ((0 > (16 * _T_i0))? 0: (16 * _T_i0));
        for (int _i0 = _ct15; (_i0 <= _ct14); _i0 = (_i0 + 1))
        {
          int _ct16 = ((((16 * _T_i1) + 16) < (((((-(Fh1) - Fh2) - Fhm1) - Fh3) + isl_floord((((Fh1 + Fh2) + Fhm1) + Y1), 2)) + 2))? ((16 * _T_i1) + 16): (((((-(Fh1) - Fh2) - Fhm1) - Fh3) + isl_floord((((Fh1 + Fh2) + Fhm1) + Y1), 2)) + 2));
          int _ct17 = ((0 > (16 * _T_i1))? 0: (16 * _T_i1));
          for (int _i1 = _ct17; (_i1 <= _ct16); _i1 = (_i1 + 1))
          {
            int _ct18 = (((K3 - 1) < ((16 * _T_i2) + 15))? (K3 - 1): ((16 * _T_i2) + 15));
            #pragma ivdep
            for (int _i2 = (16 * _T_i2); (_i2 <= _ct18); _i2 = (_i2 + 1))
            {
              double _ct19 = (double) (0.0);
              double _ct20 = _arr_11_8[(((_i0 * ((((((((-1 * Fhm1) / 2) + ((-1 * Fh1) / 2)) + (Y1 / 2)) + (-1 * Fh3)) + ((-1 * Fh2) / 2)) + 5) * K3)) + (_i1 * K3)) + _i2)];
              double _ct21 = (((double) (0.0) > _arr_11_8[(((_i0 * ((((((((-1 * Fhm1) / 2) + ((-1 * Fh1) / 2)) + (Y1 / 2)) + (-1 * Fh3)) + ((-1 * Fh2) / 2)) + 5) * K3)) + (_i1 * K3)) + _i2)])? _ct19: _ct20);
              _buf_6_9[(((((-16 * _T_i0) + _i0) * (17 * 16)) + (((-16 * _T_i1) + _i1) * 16)) + ((-16 * _T_i2) + _i2))] = _ct21;
            }
          }
        }
        if (((_T_i0 >= 0) && (_T_i1 >= 0)))
        {
          int _ct22 = ((((16 * _T_i0) + 16) < (((((-(Fwm1) - Fw1) - Fw2) - Fw3) + isl_floord(((((Fwm1 + Fw1) + Fw2) + X1) + 1), 2)) + 2))? ((16 * _T_i0) + 16): (((((-(Fwm1) - Fw1) - Fw2) - Fw3) + isl_floord(((((Fwm1 + Fw1) + Fw2) + X1) + 1), 2)) + 2));
          for (int _i0 = ((16 * _T_i0) + 1); (_i0 <= _ct22); _i0 = (_i0 + 1))
          {
            int _ct23 = ((((16 * _T_i1) + 16) < (((((-(Fh1) - Fh2) - Fhm1) - Fh3) + isl_floord(((((Fh1 + Fh2) + Fhm1) + Y1) + 1), 2)) + 2))? ((16 * _T_i1) + 16): (((((-(Fh1) - Fh2) - Fhm1) - Fh3) + isl_floord(((((Fh1 + Fh2) + Fhm1) + Y1) + 1), 2)) + 2));
            for (int _i1 = ((16 * _T_i1) + 1); (_i1 <= _ct23); _i1 = (_i1 + 1))
            {
              int _ct24 = (((K3 - 1) < ((16 * _T_i2) + 15))? (K3 - 1): ((16 * _T_i2) + 15));
              #pragma ivdep
              for (int _i2 = (16 * _T_i2); (_i2 <= _ct24); _i2 = (_i2 + 1))
              {
                _arr_11_10[(((_i0 * ((((((((-1 * Fhm1) / 2) + ((-1 * Fh1) / 2)) + (Y1 / 2)) + (-1 * Fh3)) + ((-1 * Fh2) / 2)) + 5) * K3)) + (_i1 * K3)) + _i2)] = _buf_6_9[((((-1 + ((-16 * _T_i0) + _i0)) * (17 * 16)) + ((-1 + ((-16 * _T_i1) + _i1)) * 16)) + ((-16 * _T_i2) + _i2))];
              }
            }
          }
        }
      }
    }
  }
  pool_deallocate(_arr_11_8);
  /* users : ['conv4'] */
  double * _arr_12_11;
  _arr_12_11 = (double *) (pool_allocate((sizeof(double) * (((((((((-1 * Fw4) + ((-1 * Fw1) / 2)) + ((-1 * Fwm1) / 2)) + ((-1 * Fw2) / 2)) + (X1 / 2)) + (-1 * Fw3)) + 6) * ((((((((-1 * Fh1) / 2) + ((-1 * Fh2) / 2)) + ((-1 * Fhm1) / 2)) + (-1 * Fh3)) + (-1 * Fh4)) + (Y1 / 2)) + 6)) * K4))));
  for (int _i3 = 0; (_i3 <= ((((((-(Fw4) - Fwm1) - Fw1) - Fw2) - Fw3) + isl_floord((((Fwm1 + Fw1) + Fw2) + X1), 2)) + 5)); _i3 = (_i3 + 1))
  {
    for (int _i4 = 0; (_i4 <= ((((((-(Fh1) - Fh2) - Fhm1) - Fh3) - Fh4) + isl_floord((((Fh1 + Fh2) + Fhm1) + Y1), 2)) + 5)); _i4 = (_i4 + 1))
    {
      for (int _i5 = 0; (_i5 < K4); _i5 = (_i5 + 1))
      {
        _arr_12_11[(((_i3 * (((((((((-1 * Fh1) / 2) + ((-1 * Fh2) / 2)) + ((-1 * Fhm1) / 2)) + (-1 * Fh3)) + (-1 * Fh4)) + (Y1 / 2)) + 6) * K4)) + (_i4 * K4)) + _i5)] = 0;
      }
    }
  }
  for (int _i0 = 0; (_i0 < K4); _i0 = (_i0 + 1))
  {
    for (int _i1 = 0; (_i1 < K3); _i1 = (_i1 + 1))
    {
      for (int _i2 = 0; (_i2 <= ((((((-(Fh1) - Fh2) - Fhm1) - Fh3) - Fh4) + isl_floord((((Fh1 + Fh2) + Fhm1) + Y1), 2)) + 5)); _i2 = (_i2 + 1))
      {
        for (int _i3 = 0; (_i3 <= ((((((-(Fw4) - Fwm1) - Fw1) - Fw2) - Fw3) + isl_floord((((Fwm1 + Fw1) + Fw2) + X1), 2)) + 5)); _i3 = (_i3 + 1))
        {
          for (int _i4 = 0; (_i4 < Fh4); _i4 = (_i4 + 1))
          {
            for (int _i5 = 0; (_i5 < Fw4); _i5 = (_i5 + 1))
            {
              _arr_12_11[(((_i3 * (((((((((-1 * Fh1) / 2) + ((-1 * Fh2) / 2)) + ((-1 * Fhm1) / 2)) + (-1 * Fh3)) + (-1 * Fh4)) + (Y1 / 2)) + 6) * K4)) + (_i2 * K4)) + _i0)] = (_arr_12_11[(((_i3 * (((((((((-1 * Fh1) / 2) + ((-1 * Fh2) / 2)) + ((-1 * Fhm1) / 2)) + (-1 * Fh3)) + (-1 * Fh4)) + (Y1 / 2)) + 6) * K4)) + (_i2 * K4)) + _i0)] + (_arr_11_10[((((_i3 + _i5) * ((((((((-1 * Fhm1) / 2) + ((-1 * Fh1) / 2)) + (Y1 / 2)) + (-1 * Fh3)) + ((-1 * Fh2) / 2)) + 5) * K3)) + ((_i4 + _i2) * K3)) + _i1)] * weights4[((((_i5 * ((Fh4 * K3) * K4)) + (_i4 * (K3 * K4))) + (_i1 * K4)) + _i0)]));
            }
          }
        }
      }
    }
  }
  pool_deallocate(_arr_11_10);
  /* users : ['relu4'] */
  double * _arr_10_12;
  _arr_10_12 = (double *) (pool_allocate((sizeof(double) * (((((((((-1 * Fw4) + ((-1 * Fwm1) / 2)) + ((-1 * Fw1) / 2)) + ((-1 * Fw2) / 2)) + (X1 / 2)) + (-1 * Fw3)) + 4) * ((((((((-1 * Fh1) / 2) + ((-1 * Fh2) / 2)) + ((-1 * Fhm1) / 2)) + (-1 * Fh3)) + (-1 * Fh4)) + (Y1 / 2)) + 4)) * K4))));
  for (int _i0 = 0; (_i0 <= ((((((-(Fw4) - Fw1) - Fwm1) - Fw2) - Fw3) + isl_floord((((Fw1 + Fwm1) + Fw2) + X1), 2)) + 3)); _i0 = (_i0 + 1))
  {
    for (int _i1 = 0; (_i1 <= ((((((-(Fh1) - Fh2) - Fhm1) - Fh3) - Fh4) + isl_floord((((Fh1 + Fh2) + Fhm1) + Y1), 2)) + 3)); _i1 = (_i1 + 1))
    {
      for (int _i2 = 0; (_i2 < K4); _i2 = (_i2 + 1))
      {
        double _ct25 = (double) (0.0);
        double _ct26 = _arr_12_11[(((_i0 * (((((((((-1 * Fh1) / 2) + ((-1 * Fh2) / 2)) + ((-1 * Fhm1) / 2)) + (-1 * Fh3)) + (-1 * Fh4)) + (Y1 / 2)) + 6) * K4)) + (_i1 * K4)) + _i2)];
        double _ct27 = (((double) (0.0) > _arr_12_11[(((_i0 * (((((((((-1 * Fh1) / 2) + ((-1 * Fh2) / 2)) + ((-1 * Fhm1) / 2)) + (-1 * Fh3)) + (-1 * Fh4)) + (Y1 / 2)) + 6) * K4)) + (_i1 * K4)) + _i2)])? _ct25: _ct26);
        _arr_10_12[(((_i0 * (((((((((-1 * Fh1) / 2) + ((-1 * Fh2) / 2)) + ((-1 * Fhm1) / 2)) + (-1 * Fh3)) + (-1 * Fh4)) + (Y1 / 2)) + 4) * K4)) + (_i1 * K4)) + _i2)] = _ct27;
      }
    }
  }
  pool_deallocate(_arr_12_11);
  for (int _i2 = 0; (_i2 <= ((((-(Fw4) - Fwm2) - Fw3) + isl_floord((((((((2 * Fw4) - Fwm1) - Fw1) + (2 * Fwm2)) - Fw2) + X1) + (2 * Fw3)), 4)) + 2)); _i2 = (_i2 + 1))
  {
    for (int _i3 = 0; (_i3 <= ((((-(Fh3) - Fhm2) - Fh4) + isl_floord(((((((-(Fh1) - Fh2) - Fhm1) + (2 * Fh3)) + (2 * Fhm2)) + (2 * Fh4)) + Y1), 4)) + 2)); _i3 = (_i3 + 1))
    {
      for (int _i4 = 0; (_i4 < K4); _i4 = (_i4 + 1))
      {
        maxpool2[(((_i2 * ((((((((((-1 * Fh1) / 4) + ((-1 * Fh2) / 4)) + ((-1 * Fhm1) / 4)) + ((-1 * Fh3) / 2)) + ((-1 * Fhm2) / 2)) + ((-1 * Fh4) / 2)) + (Y1 / 4)) + 3) * K4)) + (_i3 * K4)) + _i4)] = 0;
      }
    }
  }
  for (int _i0 = 0; (_i0 < K4); _i0 = (_i0 + 1))
  {
    for (int _i1 = 0; (_i1 <= ((((-(Fh3) - Fhm2) - Fh4) + isl_floord(((((((-(Fh1) - Fh2) - Fhm1) + (2 * Fh3)) + (2 * Fhm2)) + (2 * Fh4)) + Y1), 4)) + 2)); _i1 = (_i1 + 1))
    {
      for (int _i2 = 0; (_i2 <= ((((-(Fw4) - Fwm2) - Fw3) + isl_floord((((((((2 * Fw4) - Fwm1) - Fw1) + (2 * Fwm2)) - Fw2) + X1) + (2 * Fw3)), 4)) + 2)); _i2 = (_i2 + 1))
      {
        for (int _i3 = 0; (_i3 < Fhm2); _i3 = (_i3 + 1))
        {
          for (int _i4 = 0; (_i4 < Fwm2); _i4 = (_i4 + 1))
          {
            maxpool2[(((_i2 * ((((((((((-1 * Fh1) / 4) + ((-1 * Fh2) / 4)) + ((-1 * Fhm1) / 4)) + ((-1 * Fh3) / 2)) + ((-1 * Fhm2) / 2)) + ((-1 * Fh4) / 2)) + (Y1 / 4)) + 3) * K4)) + (_i1 * K4)) + _i0)] = ((maxpool2[(((_i2 * ((((((((((-1 * Fh1) / 4) + ((-1 * Fh2) / 4)) + ((-1 * Fhm1) / 4)) + ((-1 * Fh3) / 2)) + ((-1 * Fhm2) / 2)) + ((-1 * Fh4) / 2)) + (Y1 / 4)) + 3) * K4)) + (_i1 * K4)) + _i0)] > _arr_10_12[((((_i4 + (2 * _i2)) * (((((((((-1 * Fh1) / 2) + ((-1 * Fh2) / 2)) + ((-1 * Fhm1) / 2)) + (-1 * Fh3)) + (-1 * Fh4)) + (Y1 / 2)) + 4) * K4)) + (((2 * _i1) + _i3) * K4)) + _i0)])? maxpool2[(((_i2 * ((((((((((-1 * Fh1) / 4) + ((-1 * Fh2) / 4)) + ((-1 * Fhm1) / 4)) + ((-1 * Fh3) / 2)) + ((-1 * Fhm2) / 2)) + ((-1 * Fh4) / 2)) + (Y1 / 4)) + 3) * K4)) + (_i1 * K4)) + _i0)]: _arr_10_12[((((_i4 + (2 * _i2)) * (((((((((-1 * Fh1) / 2) + ((-1 * Fh2) / 2)) + ((-1 * Fhm1) / 2)) + (-1 * Fh3)) + (-1 * Fh4)) + (Y1 / 2)) + 4) * K4)) + (((2 * _i1) + _i3) * K4)) + _i0)]);
          }
        }
      }
    }
  }
  pool_deallocate(_arr_10_12);
}