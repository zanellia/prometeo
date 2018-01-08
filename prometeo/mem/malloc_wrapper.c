#include <stdlib.h>

void prmt_malloc(double **mem, int size){
	mem = malloc(sizeof(double)*size);
	return;
}	
