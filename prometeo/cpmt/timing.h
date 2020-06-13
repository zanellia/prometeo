/**************************************************************************************************
*                                                                                                 *
* This file is part of BLASFEO.                                                                   *
*                                                                                                 *
* BLASFEO -- BLAS For Embedded Optimization.                                                      *
* Copyright (C) 2019 by Gianluca Frison.                                                          *
* Developed at IMTEK (University of Freiburg) under the supervision of Moritz Diehl.              *
* All rights reserved.                                                                            *
*                                                                                                 *
* The 2-Clause BSD License                                                                        *
*                                                                                                 *
* Redistribution and use in source and binary forms, with or without                              *
* modification, are permitted provided that the following conditions are met:                     *
*                                                                                                 *
* 1. Redistributions of source code must retain the above copyright notice, this                  *
*    list of conditions and the following disclaimer.                                             *
* 2. Redistributions in binary form must reproduce the above copyright notice,                    *
*    this list of conditions and the following disclaimer in the documentation                    *
*    and/or other materials provided with the distribution.                                       *
*                                                                                                 *
* THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND                 *
* ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED                   *
* WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE                          *
* DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR                 *
* ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES                  *
* (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;                    *
* LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND                     *
* ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT                      *
* (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS                   *
* SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.                                    *
*                                                                                                 *
* Author: Gianluca Frison, gianluca.frison (at) imtek.uni-freiburg.de                             *
*                                                                                                 *
**************************************************************************************************/

#ifndef PROMETEO_TIMING_H_
#define PROMETEO_TIMING_H_

//#include <stdbool.h>

#if (defined _WIN32 || defined _WIN64) && !(defined __MINGW32__ || defined __MINGW64__)

	/* Use Windows QueryPerformanceCounter for timing. */
	#include <Windows.h>

	/** A structure for keeping internal timer data. */
	typedef struct prometeo_timer_ {
		LARGE_INTEGER tic;
		LARGE_INTEGER toc;
		LARGE_INTEGER freq;
	} prometeo_timer;

#elif(defined __APPLE__)

	#include <mach/mach_time.h>

	/** A structure for keeping internal timer data. */
	typedef struct prometeo_timer_ {
		uint64_t tic;
		uint64_t toc;
		mach_timebase_info_data_t tinfo;
	} prometeo_timer;

#elif(defined __DSPACE__)

	#include <brtenv.h>

	typedef struct prometeo_timer_ {
		double time;
	} prometeo_timer;

#elif(defined __XILINX_NONE_ELF__)

	#include "xtime_l.h"

	typedef struct prometeo_timer_ {
		uint64_t tic;
		uint64_t toc;
	} prometeo_timer;

#else

	/* Use POSIX clock_gettime() for timing on non-Windows machines. */
	#include <time.h>

	#if __STDC_VERSION__ >= 199901L  // C99 Mode

		#include <sys/stat.h>
		#include <sys/time.h>

		typedef struct prometeo_timer_ {
			struct timeval tic;
			struct timeval toc;
		} prometeo_timer;

	#else  // ANSI C Mode

		/** A structure for keeping internal timer data. */
		typedef struct prometeo_timer_ {
			struct timespec tic;
			struct timespec toc;
		} prometeo_timer;

	#endif  // __STDC_VERSION__ >= 199901L

#endif  // (defined _WIN32 || defined _WIN64)

/** A function for measurement of the current time. */
void prometeo_tic(prometeo_timer* t);

/** A function which returns the elapsed time. */
double prometeo_toc(prometeo_timer* t);

#endif  // PROMETEO_TIMING_H_
