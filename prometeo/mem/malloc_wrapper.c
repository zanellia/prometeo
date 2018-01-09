#include <stdio.h>
#include <stdlib.h>

void prmt_malloc(void **mem, int n_bytes){
	*mem = malloc(n_bytes);
	return;
}	
