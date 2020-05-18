module riccati

using LinearAlgebra

# Riccat recursion

function riccati_trf(N, nx, nu, BAt, RSQ, L, LN, BAtL, M)

	LN = copy(RSQ[nu+1:nu+nx, nu+1:nu+nx]);
	LAPACK.potrf!('L', LN);

	for ii in 1:N
		BAtL = copy(BAt);
		if ii==1
#			BLAS.gemm!('N', 'N', 1.0, BAt, LN, 0.0, BAtL);
			BLAS.trmm!('R', 'L', 'N', 'N', 1.0, LN, BAtL);
		else
#			BLAS.gemm!('N', 'N', 1.0, BAt, L[nu+1:nu+nx,nu+1:nu+nx,N+2-ii], 0.0, BAtL);
#			display(L[:,:,N+2-ii])
#			println()
#			BLAS.trmm!('R', 'L', 'N', 'N', 1.0, L[nu+1:nu+nx,nu+1:nu+nx,N+2-ii], BAtL);
			BLAS.trmm!('R', 'L', 'N', 'N', 1.0, view(L, nu+1:nu+nx, nu+1:nu+nx, N+2-ii), BAtL);
		end
#		M = copy(RSQ);
#		BLAS.syrk!('L', 'N', 1.0, BAtL, 1.0, M);
#		LAPACK.potrf!('L', M);
#		L[:,:,N+1-ii] = copy(M);
		L[:,:,N+1-ii] = copy(RSQ);
		MM = view(L, :, :, N+1-ii);
		BLAS.syrk!('L', 'N', 1.0, BAtL, 1.0, MM);
		LAPACK.potrf!('L', MM);
	end

#display(L)
#println()

end

export riccati_trf

end
