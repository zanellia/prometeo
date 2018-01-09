#include <stdio.h>
#include <stdlib.h>

void prmt_malloc(double **mem, int size){
	*mem = malloc(sizeof(double)*size);
	printf("size = %i", size);
	return;
}	
