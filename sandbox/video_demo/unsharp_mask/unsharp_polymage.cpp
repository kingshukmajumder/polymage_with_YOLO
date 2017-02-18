#include <stdio.h>
#include <stdlib.h>
#include <malloc.h>
#include <cmath>
#include <string.h>
#include "../simple_pool_allocator.h"
#include "../utils/data_layout_transformer.h"
#define isl_min(x,y) ((x) < (y) ? (x) : (y))
#define isl_max(x,y) ((x) > (y) ? (x) : (y))
#define isl_floord(n,d) (((n)<0) ? -((-(n)+(d)-1)/(d)) : (n)/(d))

extern "C" void pipeline_opt(int C, int R, float threshold, float weight, void * img_void_arg, void * mask_void_arg)
{
  unsigned char * img_flip;
  img_flip = (unsigned char *) (img_void_arg);
  float * mask_flip;
  mask_flip = (float *) (mask_void_arg);
  float * img = (float *)pool_allocate(sizeof(float) * 3 * (R+4) * (C+4));

  //data_layout_transform(img, img_flip, 255.0f, R+4, C+4, 3);
  data_layout_transform_char_to_float(img, img_flip, 255.0f, R+4, C+4, 3);

  #pragma omp parallel for schedule(static)
  for (int _T_i1 = 0; (_T_i1 <= (R / 16)); _T_i1 = (_T_i1 + 1))
  {
    /* users : ['sharpen', 'blurx'] */
    float _buf_1_0[((3 * 16) * 22)];
    /* users : ['blury'] */
    float _buf_1_1[((3 * 16) * 22)];
    for (int _T_i2 = -1; (_T_i2 <= (C / 16)); _T_i2 = (_T_i2 + 1))
    {
      for (int _i0 = 0; (_i0 <= 2); _i0 = (_i0 + 1))
      {
        int _ct0 = ((R < ((16 * _T_i1) + 15))? R: ((16 * _T_i1) + 15));
        int _ct1 = ((2 > (16 * _T_i1))? 2: (16 * _T_i1));
        for (int _i1 = _ct1; (_i1 <= _ct0); _i1 = (_i1 + 1))
        {
          int _ct2 = ((C < ((16 * _T_i2) + 21))? C: ((16 * _T_i2) + 21));
          int _ct3 = ((1 > (16 * _T_i2))? 1: (16 * _T_i2));
          #pragma ivdep
          for (int _i2 = _ct3; (_i2 <= _ct2); _i2 = (_i2 + 1))
          {
            _buf_1_0[(((_i0 * (16 * 22)) + (((-16 * _T_i1) + _i1) * 22)) + ((-16 * _T_i2) + _i2))] = (((((img[(((_i0 * ((4 + R) * (4 + C))) + ((-2 + _i1) * (4 + C))) + _i2)] + (img[(((_i0 * ((4 + R) * (4 + C))) + ((-1 + _i1) * (4 + C))) + _i2)] * 4.0)) + (img[(((_i0 * ((4 + R) * (4 + C))) + (_i1 * (4 + C))) + _i2)] * 6.0)) + (img[(((_i0 * ((4 + R) * (4 + C))) + ((1 + _i1) * (4 + C))) + _i2)] * 4.0)) + img[(((_i0 * ((4 + R) * (4 + C))) + ((2 + _i1) * (4 + C))) + _i2)]) * 0.0625);
          }
        }
      }
      for (int _i0 = 0; (_i0 <= 2); _i0 = (_i0 + 1))
      {
        int _ct4 = ((R < ((16 * _T_i1) + 15))? R: ((16 * _T_i1) + 15));
        int _ct5 = ((2 > (16 * _T_i1))? 2: (16 * _T_i1));
        for (int _i1 = _ct5; (_i1 <= _ct4); _i1 = (_i1 + 1))
        {
          int _ct6 = ((C < ((16 * _T_i2) + 20))? C: ((16 * _T_i2) + 20));
          int _ct7 = ((2 > ((16 * _T_i2) + 1))? 2: ((16 * _T_i2) + 1));
          #pragma ivdep
          for (int _i2 = _ct7; (_i2 <= _ct6); _i2 = (_i2 + 1))
          {
            _buf_1_1[(((_i0 * (16 * 22)) + (((-16 * _T_i1) + _i1) * 22)) + ((-16 * _T_i2) + _i2))] = (((((_buf_1_0[(((_i0 * (16 * 22)) + (((-16 * _T_i1) + _i1) * 22)) + (-2 + ((-16 * _T_i2) + _i2)))] + (_buf_1_0[(((_i0 * (16 * 22)) + (((-16 * _T_i1) + _i1) * 22)) + (-1 + ((-16 * _T_i2) + _i2)))] * 4.0)) + (_buf_1_0[(((_i0 * (16 * 22)) + (((-16 * _T_i1) + _i1) * 22)) + ((-16 * _T_i2) + _i2))] * 6.0)) + (_buf_1_0[(((_i0 * (16 * 22)) + (((-16 * _T_i1) + _i1) * 22)) + (1 + ((-16 * _T_i2) + _i2)))] * 4.0)) + _buf_1_0[(((_i0 * (16 * 22)) + (((-16 * _T_i1) + _i1) * 22)) + (2 + ((-16 * _T_i2) + _i2)))]) * 0.0625);
          }
        }
      }
      for (int _i0 = 0; (_i0 <= 2); _i0 = (_i0 + 1))
      {
        int _ct8 = ((R < ((16 * _T_i1) + 15))? R: ((16 * _T_i1) + 15));
        int _ct9 = ((2 > (16 * _T_i1))? 2: (16 * _T_i1));
        for (int _i1 = _ct9; (_i1 <= _ct8); _i1 = (_i1 + 1))
        {
          int _ct10 = ((C < ((16 * _T_i2) + 19))? C: ((16 * _T_i2) + 19));
          int _ct11 = ((2 > ((16 * _T_i2) + 2))? 2: ((16 * _T_i2) + 2));
          #pragma ivdep
          for (int _i2 = _ct11; (_i2 <= _ct10); _i2 = (_i2 + 1))
          {
            _buf_1_0[(((_i0 * (16 * 22)) + (((-16 * _T_i1) + _i1) * 22)) + ((-16 * _T_i2) + _i2))] = ((img[(((_i0 * ((4 + R) * (4 + C))) + (_i1 * (4 + C))) + _i2)] * (1 + weight)) - (_buf_1_1[(((_i0 * (16 * 22)) + (((-16 * _T_i1) + _i1) * 22)) + ((-16 * _T_i2) + _i2))] * weight));
          }
        }
      }
      for (int _i0 = 0; (_i0 <= 2); _i0 = (_i0 + 1))
      {
        int _ct12 = ((R < ((16 * _T_i1) + 15))? R: ((16 * _T_i1) + 15));
        int _ct13 = ((2 > (16 * _T_i1))? 2: (16 * _T_i1));
        for (int _i1 = _ct13; (_i1 <= _ct12); _i1 = (_i1 + 1))
        {
          int _ct14 = ((C < ((16 * _T_i2) + 18))? C: ((16 * _T_i2) + 18));
          int _ct15 = ((2 > ((16 * _T_i2) + 3))? 2: ((16 * _T_i2) + 3));
          #pragma ivdep
          for (int _i2 = _ct15; (_i2 <= _ct14); _i2 = (_i2 + 1))
          {
            float _ct16 = img[(((_i0 * ((4 + R) * (4 + C))) + (_i1 * (4 + C))) + _i2)];
            float _ct17 = _buf_1_0[(((_i0 * (16 * 22)) + (((-16 * _T_i1) + _i1) * 22)) + ((-16 * _T_i2) + _i2))];
            float _ct18 = ((std::abs((img[(((_i0 * ((4 + R) * (4 + C))) + (_i1 * (4 + C))) + _i2)] - _buf_1_1[(((_i0 * (16 * 22)) + (((-16 * _T_i1) + _i1) * 22)) + ((-16 * _T_i2) + _i2))])) < threshold)? _ct16: _ct17);
            mask_flip[((((_i1 - 2) * (3 * C)) + ((_i2 - 2) * 3)) + (_i0))] = _ct18;
          }
        }
      }
    }
  }

  pool_deallocate(img);

}
