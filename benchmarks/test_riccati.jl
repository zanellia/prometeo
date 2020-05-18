include("./riccati.jl")
using .riccati

# main script

nmass = 146;
nrep = 10

nx = 2*nmass;
nu = nmass;
N = 5;

# data

# mass spring system
Ts = 0.5;

Ac = zeros(nx, nx);
for ii in 1:nmass
	Ac[ii, nmass+ii] = 1.0;
end
for ii in 1:nmass
	Ac[nmass+ii, ii] = -2.0;
end
for ii in 1:nmass-1
	Ac[nmass+ii+1, ii] = 1.0;
end
for ii in 1:nmass-1
	Ac[nmass+ii, ii+1] = 1.0;
end

Bc = zeros(nx, nu);
for ii in 1:nu
	Bc[nmass+ii, ii] = 1.0;
end

#display(Ac)
#println()
#display(Bc)
#println()

MM = [ Ts*Ac Ts*Bc; zeros(nu, nx+nu) ];

#display(MM)
#println()

#MM = exp( MM )
MM = randn(nu+nx, nu+nx);

#display(MM)
#println()

A = MM[1:nx,1:nx];
B = MM[1:nx, nx+1:end];

#display(A)
#println()
#display(B)
#println()

Q = zeros(nx, nx)
for ii in 1:nx
	Q[ii, ii] = 1.0
end

R = zeros(nu, nu)
for ii in 1:nu
	R[ii, ii] = 2.0
end

#display(Q)
#println()
#display(R)
#println()

x0 = zeros(nx, 1)
x0[1] = 3.5
x0[2] = 3.5

#display(x0)
#println()


# work matrices

BAt = [transpose(B); transpose(A)];
#display(BAt)
#println()
RSQ = [R zeros(nu,nx); zeros(nx,nu) Q];

BAtL = zeros(nu+nx, nx);
L = zeros(nu+nx, nu+nx, N);
LN = zeros(nx, nx);
M = zeros(nu+nx, nu+nx);


# riccati recursion, square root algorithm

for rep in 1:nrep
	riccati_trf(N, nx, nu, BAt, RSQ, L, LN, BAtL, M);
end

time_start = time_ns()

for rep in 1:nrep
	riccati_trf(N, nx, nu, BAt, RSQ, L, LN, BAtL, M);
end

time_end = time_ns()

println((time_end-time_start)/nrep*1e-9)



#display(L)
#println()
#display(LN)
#println()
