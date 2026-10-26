# B5 2025 PS2 Updated - Questions and Answers

## Q3 - Constancy of the Four-Velocity Norm Along a Geodesic

### Question

3) Using the geodesic equation, show that the norm of the four-velocity, $U^{\mu} U_{\mu}$, is constant along a geodesic.

### Answer

Let the curve be parametrised by proper time $\tau$, and define the four-velocity

$$
U^\mu=\frac{dx^\mu}{d\tau}.
$$

The geodesic equation may be written in the usual component form as

$$
\frac{dU^\mu}{d\tau}
+\Gamma^\mu_{\rho\sigma}U^\rho U^\sigma=0.
$$

Equivalently, using the covariant derivative along the curve,

$$
\frac{D}{D\tau}=U^\rho\nabla_\rho,
$$

the same equation is

$$
\frac{D U^\mu}{D\tau}=U^\rho\nabla_\rho U^\mu=0.
$$

We want to show that

$$
U^\mu U_\mu
$$

is constant along the geodesic. Since $U^\mu U_\mu$ is a scalar, its covariant derivative along the curve is just its ordinary derivative:

$$
\frac{D}{D\tau}\left(U^\mu U_\mu\right)
=\frac{d}{d\tau}\left(U^\mu U_\mu\right).
$$

Now use the Leibniz rule:

$$
\frac{D}{D\tau}\left(U^\mu U_\mu\right)
=
\frac{D U^\mu}{D\tau}U_\mu
+U^\mu\frac{D U_\mu}{D\tau}.
$$

The first term vanishes directly from the geodesic equation:

$$
\frac{D U^\mu}{D\tau}=0.
$$

For the second term, use metric compatibility. Since

$$
U_\mu=g_{\mu\nu}U^\nu,
$$

we have

$$
\frac{D U_\mu}{D\tau}
=
\frac{D}{D\tau}\left(g_{\mu\nu}U^\nu\right).
$$

By the product rule,

$$
\frac{D U_\mu}{D\tau}
=
\frac{D g_{\mu\nu}}{D\tau}U^\nu
+g_{\mu\nu}\frac{D U^\nu}{D\tau}.
$$

But the Levi-Civita connection is metric-compatible:

$$
\nabla_\rho g_{\mu\nu}=0.
$$

Therefore

$$
\frac{D g_{\mu\nu}}{D\tau}
=U^\rho\nabla_\rho g_{\mu\nu}=0.
$$

The second term also vanishes by the geodesic equation:

$$
g_{\mu\nu}\frac{D U^\nu}{D\tau}=0.
$$

So

$$
\frac{D U_\mu}{D\tau}=0.
$$

Hence

$$
\frac{D}{D\tau}\left(U^\mu U_\mu\right)
=0.
$$

Since this quantity is a scalar,

$$
\frac{d}{d\tau}\left(U^\mu U_\mu\right)=0.
$$

Therefore

$$
U^\mu U_\mu=\text{constant}
$$

along a geodesic.

Equivalently, in fully expanded form,

$$
U^\mu U_\mu=g_{\mu\nu}U^\mu U^\nu.
$$

Differentiating with respect to $\tau$ gives

$$
\frac{d}{d\tau}\left(g_{\mu\nu}U^\mu U^\nu\right)
=
\partial_\rho g_{\mu\nu}U^\rho U^\mu U^\nu
+g_{\mu\nu}\frac{dU^\mu}{d\tau}U^\nu
+g_{\mu\nu}U^\mu\frac{dU^\nu}{d\tau}.
$$

Because $g_{\mu\nu}=g_{\nu\mu}$, the last two terms are equal after relabelling dummy indices, so

$$
\frac{d}{d\tau}\left(g_{\mu\nu}U^\mu U^\nu\right)
=
\partial_\rho g_{\mu\nu}U^\rho U^\mu U^\nu
+2g_{\mu\nu}U^\mu\frac{dU^\nu}{d\tau}.
$$

Using the geodesic equation,

$$
\frac{dU^\nu}{d\tau}=-\Gamma^\nu_{\alpha\beta}U^\alpha U^\beta,
$$

this becomes

$$
\frac{d}{d\tau}\left(g_{\mu\nu}U^\mu U^\nu\right)
=
\partial_\rho g_{\mu\nu}U^\rho U^\mu U^\nu
-2g_{\mu\nu}\Gamma^\nu_{\alpha\beta}U^\mu U^\alpha U^\beta.
$$

Rename the dummy indices $\alpha\to\rho$, $\beta\to\nu$:

$$
\frac{d}{d\tau}\left(g_{\mu\nu}U^\mu U^\nu\right)
=
\partial_\rho g_{\mu\nu}U^\rho U^\mu U^\nu
-2g_{\mu\lambda}\Gamma^\lambda_{\rho\nu}U^\mu U^\rho U^\nu.
$$

Now use metric compatibility in component form:

$$
\nabla_\rho g_{\mu\nu}
=
\partial_\rho g_{\mu\nu}
-g_{\lambda\nu}\Gamma^\lambda_{\mu\rho}
-g_{\mu\lambda}\Gamma^\lambda_{\nu\rho}
=0.
$$

Thus

$$
\partial_\rho g_{\mu\nu}
=
g_{\lambda\nu}\Gamma^\lambda_{\mu\rho}
+g_{\mu\lambda}\Gamma^\lambda_{\nu\rho}.
$$

Multiplying by $U^\rho U^\mu U^\nu$, and using the symmetry of $U^\rho U^\mu U^\nu$ under interchange of dummy indices, the two terms on the right give equal contributions:

$$
\partial_\rho g_{\mu\nu}U^\rho U^\mu U^\nu
=
2g_{\mu\lambda}\Gamma^\lambda_{\rho\nu}U^\mu U^\rho U^\nu.
$$

This exactly cancels the connection term above, leaving

$$
\frac{d}{d\tau}\left(g_{\mu\nu}U^\mu U^\nu\right)=0.
$$

So the component calculation agrees with the covariant proof:

$$
\boxed{\frac{d}{d\tau}\left(U^\mu U_\mu\right)=0.}
$$

For a massive particle parametrised by proper time, the constant is fixed by the interval convention:

$$
U^\mu U_\mu=-c^2
$$

in the sign convention used by the lecture notes. The problem only asks for constancy, so the essential result is that the geodesic equation preserves the norm of $U^\mu$ along the motion.

### Follow-up Question

#### Why is $\frac{D}{D\tau}=U^\rho\nabla_\rho$?

The short answer is: $\nabla_\rho$ means "covariantly differentiate in the $x^\rho$ coordinate direction", while $U^\rho=dx^\rho/d\tau$ is the tangent vector to the worldline. Therefore $U^\rho\nabla_\rho$ is the covariant derivative in the direction tangent to the curve. That is exactly what $D/D\tau$ means.

Start with the ordinary chain rule for a scalar function $f(x)$ along a curve $x^\mu(\tau)$. Along the curve,

$$
\frac{df}{d\tau}
=
\frac{dx^\rho}{d\tau}\frac{\partial f}{\partial x^\rho}.
$$

Since

$$
U^\rho=\frac{dx^\rho}{d\tau},
$$

this is

$$
\frac{df}{d\tau}=U^\rho\partial_\rho f.
$$

For a scalar, the covariant derivative is the same as the partial derivative:

$$
\nabla_\rho f=\partial_\rho f.
$$

So for a scalar,

$$
\frac{Df}{D\tau}
=
\frac{df}{d\tau}
=
U^\rho\nabla_\rho f.
$$

For a vector, the same idea holds, but the derivative must be upgraded from an ordinary derivative to a covariant derivative. Let $A^\mu(\tau)$ be a vector field evaluated along the curve. The covariant derivative of $A^\mu$ in the coordinate direction $x^\rho$ is

$$
\nabla_\rho A^\mu
=
\partial_\rho A^\mu+\Gamma^\mu_{\lambda\rho}A^\lambda.
$$

Now contract this with the tangent vector $U^\rho$:

$$
U^\rho\nabla_\rho A^\mu
=
U^\rho\partial_\rho A^\mu
+U^\rho\Gamma^\mu_{\lambda\rho}A^\lambda.
$$

The first term is just the ordinary chain rule along the curve:

$$
U^\rho\partial_\rho A^\mu
=
\frac{dx^\rho}{d\tau}\frac{\partial A^\mu}{\partial x^\rho}
=
\frac{dA^\mu}{d\tau}.
$$

Therefore

$$
U^\rho\nabla_\rho A^\mu
=
\frac{dA^\mu}{d\tau}
+\Gamma^\mu_{\lambda\rho}A^\lambda U^\rho.
$$

But this is exactly the definition of the covariant derivative of a vector along a path:

$$
\frac{D A^\mu}{D\tau}
\equiv
\frac{dA^\mu}{d\tau}
+\Gamma^\mu_{\lambda\rho}A^\lambda\frac{dx^\rho}{d\tau}.
$$

Since $U^\rho=dx^\rho/d\tau$, we have

$$
\frac{D A^\mu}{D\tau}
=
U^\rho\nabla_\rho A^\mu.
$$

Because $A^\mu$ was arbitrary, we usually write the operator identity

$$
\boxed{\frac{D}{D\tau}=U^\rho\nabla_\rho.}
$$

This notation means "take the covariant derivative in the direction of the curve's tangent vector". In coordinate-free notation, if $U$ is the tangent vector to the curve, then this is the same statement as

$$
\frac{D A}{D\tau}=\nabla_U A.
$$

For the geodesic problem, we apply this to $A^\mu=U^\mu$. Then

$$
\frac{D U^\mu}{D\tau}
=
U^\rho\nabla_\rho U^\mu.
$$

Thus the geodesic equation can be written either as

$$
\frac{D U^\mu}{D\tau}=0
$$

or as

$$
U^\rho\nabla_\rho U^\mu=0.
$$

They are the same equation. The first notation emphasizes "differentiate the four-velocity along the particle's own worldline"; the second notation shows explicitly that this derivative is the tangent vector $U^\rho$ contracted into the covariant derivative $\nabla_\rho$.


#### Can we get $\frac{D A^\mu}{D\tau}$ by taking $X^\sigma=\tau$?

The answer is: not quite. The formula you know,

$$
\boxed{\frac{DA^{\mu}}{DX^{\sigma}}\equiv \partial_{\sigma} A^{\mu} + \Gamma_{\sigma \rho}^{\mu}A^{\rho}},
$$

is really the coordinate-direction covariant derivative:

$$
\nabla_\sigma A^\mu
=
\partial_\sigma A^\mu+\Gamma^\mu_{\sigma\rho}A^\rho.
$$

Here $\sigma$ labels one of the spacetime coordinate directions. For example, $\sigma=0$ means differentiate in the $X^0$ direction, $\sigma=1$ means differentiate in the $X^1$ direction, and so on. But $\tau$ is usually not one of the spacetime coordinates. It is a parameter along a particular curve:

$$
X^\mu=X^\mu(\tau).
$$

So we should not simply set

$$
X^\sigma=\tau.
$$

That would confuse a coordinate label $X^\sigma$ with a curve parameter $\tau$. The right operation is instead: take the covariant differential in all coordinate directions, then restrict it to the curve.

Start from your formula, but write it as

$$
DA^\mu
=
\left(\partial_\sigma A^\mu+\Gamma^\mu_{\sigma\rho}A^\rho\right)dX^\sigma.
$$

This is the covariant version of the ordinary differential

$$
dA^\mu=\partial_\sigma A^\mu\,dX^\sigma.
$$

The only difference is that for a vector, the covariant differential has the connection correction:

$$
DA^\mu
=
\nabla_\sigma A^\mu\,dX^\sigma.
$$

Now put the vector field on a curve $X^\mu(\tau)$. Along this curve, each coordinate differential is

$$
dX^\sigma
=
\frac{dX^\sigma}{d\tau}d\tau.
$$

Therefore

$$
DA^\mu
=
\nabla_\sigma A^\mu
\frac{dX^\sigma}{d\tau}d\tau.
$$

Divide by $d\tau$:

$$
\frac{DA^\mu}{D\tau}
=
\frac{dX^\sigma}{d\tau}\nabla_\sigma A^\mu.
$$

But by definition the tangent vector to the curve is

$$
U^\sigma=\frac{dX^\sigma}{d\tau}.
$$

So

$$
\frac{DA^\mu}{D\tau}
=
U^\sigma\nabla_\sigma A^\mu.
$$

Writing it out explicitly,

$$
\frac{DA^\mu}{D\tau}
=
U^\sigma
\left(
\partial_\sigma A^\mu+\Gamma^\mu_{\sigma\rho}A^\rho
\right).
$$

The first term is

$$
U^\sigma\partial_\sigma A^\mu
=
\frac{dX^\sigma}{d\tau}\frac{\partial A^\mu}{\partial X^\sigma}
=
\frac{dA^\mu}{d\tau},
$$

by the ordinary chain rule. The second term is

$$
U^\sigma\Gamma^\mu_{\sigma\rho}A^\rho
=
\Gamma^\mu_{\sigma\rho}A^\rho\frac{dX^\sigma}{d\tau}.
$$

Thus

$$
\frac{DA^\mu}{D\tau}
=
\frac{dA^\mu}{d\tau}
+\Gamma^\mu_{\sigma\rho}A^\rho\frac{dX^\sigma}{d\tau}.
$$

This is the same formula as before, just with dummy indices named differently.

The safest way to remember the relationship is:

$$
\boxed{
\text{along-path derivative}
=
\text{tangent vector} \cdot \text{coordinate covariant derivative}
}
$$

or, in symbols,

$$
\boxed{
\frac{D}{D\tau}
=
\frac{dX^\sigma}{d\tau}\nabla_\sigma
=
U^\sigma\nabla_\sigma.
}
$$

So your instinct is close: we do use $\tau$, but not by replacing one coordinate $X^\sigma$ with $\tau$. Instead, we use the curve $X^\sigma(\tau)$ and the chain rule:

$$
dX^\sigma=\frac{dX^\sigma}{d\tau}d\tau.
$$

That is why every coordinate-direction covariant derivative $\nabla_\sigma A^\mu$ gets weighted by the corresponding velocity component $dX^\sigma/d\tau$.

## Q4 - Geodesics and Conservation Laws

### Question

4) Geodesics and conservation laws.

4a) Using the geodesic equation in the form $D U^{\mu} / D \tau=0$, where $U^{\mu}=d x^{\mu} / d \tau$ is the four-velocity, find the equation satisfied by $x_{\mu}=g_{\mu \nu} x^{\nu}$. Show that for a metric whose components are time-independent, $U_{0}$ is a constant of motion.

4b) Show that in flat space-time, the conservation law for the four-momentum $p$ of a freely moving massive particle can be written as $\nabla_{p} p=0$. Show that the particles move along time-like geodesics.

4c) Suppose that the metric components $g_{\mu \nu}(x)$ are independent of the particular coordinate, say, $x^{1}$. Show that for a particle moving along a geodesic, the component $p_{1}$ of $p_{\mu}=g_{\mu \nu} p^{\nu}$, where $p^{\mu}$ is the particle's four-momentum, is constant along the geodesic.\\

### Answer

The notation in 4a is almost certainly intended to refer to the lowered four-velocity

$$
U_\mu=g_{\mu\nu}U^\nu,
$$

since the conclusion to be shown is that $U_0$ is conserved, and the lecture notes give the lowered-index geodesic equation precisely in this form. I therefore derive the equation for $U_\mu$ and then translate it to the momentum $p_\mu$ in parts 4b-4c.

For a geodesic,

$$
\frac{D U^\mu}{D\tau}=0.
$$

Lowering the index gives

$$
\frac{D U_\mu}{D\tau}=0,
$$

and for a covector this means

$$
\frac{D U_\mu}{D\tau}
=
\frac{dU_\mu}{d\tau}-\Gamma^\rho_{\mu\nu}U_\rho U^\nu
=0.
$$

Hence

$$
\frac{dU_\mu}{d\tau}
=
\Gamma^\rho_{\mu\nu}U_\rho U^\nu.
$$

Now substitute $U_\rho=g_{\rho\sigma}U^\sigma$ and the Christoffel-symbol formula:

$$
\Gamma^\rho_{\mu\nu}g_{\rho\sigma}
=
\frac12\left(
\partial_\mu g_{\sigma\nu}
+\partial_\nu g_{\sigma\mu}
-\partial_\sigma g_{\mu\nu}
\right).
$$

Therefore

$$
\frac{dU_\mu}{d\tau}
=
\frac12
\left(
\partial_\mu g_{\sigma\nu}
+\partial_\nu g_{\sigma\mu}
-\partial_\sigma g_{\mu\nu}
\right)
U^\sigma U^\nu.
$$

Because $U^\sigma U^\nu$ is symmetric under $\sigma\leftrightarrow\nu$, the last two terms cancel after relabelling dummy indices:

$$
\frac12\,\partial_\nu g_{\sigma\mu}U^\sigma U^\nu
-\frac12\,\partial_\sigma g_{\mu\nu}U^\sigma U^\nu
=0.
$$

So the lowered geodesic equation becomes

$$
\boxed{
\frac{dU_\mu}{d\tau}
=
\frac12\,\partial_\mu g_{\rho\nu}\,U^\rho U^\nu.
}
$$

This is the equation required in 4a.

If the metric is time-independent, then

$$
\partial_0 g_{\rho\nu}=0.
$$

Setting $\mu=0$ in the boxed equation gives

$$
\frac{dU_0}{d\tau}
=
\frac12\,\partial_0 g_{\rho\nu}\,U^\rho U^\nu
=0,
$$

so

$$
\boxed{U_0=\text{constant}.}
$$

For 4b, let the particle have rest mass $m$, so

$$
p^\mu=mU^\mu,
\qquad
p_\mu=mU_\mu,
$$

with $m$ constant for a freely moving massive particle. In flat spacetime, in inertial Cartesian coordinates, the Levi-Civita connection vanishes, so conservation of four-momentum is simply

$$
\frac{dp^\mu}{d\tau}=0.
$$

But in those same coordinates,

$$
\frac{D p^\mu}{D\tau}
=
U^\nu\nabla_\nu p^\mu
=
\frac{1}{m}p^\nu\nabla_\nu p^\mu.
$$

Therefore

$$
\frac{D p^\mu}{D\tau}=0
\qquad\Longleftrightarrow\qquad
p^\nu\nabla_\nu p^\mu=0,
$$

that is,

$$
\boxed{\nabla_p p=0.}
$$

Now use $p^\mu=mU^\mu$:

$$
\nabla_p p
=
\nabla_{mU}(mU)
=
m^2\nabla_U U,
$$

since $m$ is constant. Hence

$$
\nabla_p p=0
\qquad\Longrightarrow\qquad
\nabla_U U=0.
$$

But

$$
\nabla_U U=0
$$

is exactly the coordinate-free geodesic equation. So the worldline of a freely moving massive particle is a geodesic.

Because the particle is massive,

$$
p^\mu p_\mu=-m^2c^2<0.
$$

Equivalently,

$$
U^\mu U_\mu=-c^2<0,
$$

so the tangent vector is time-like. Therefore the particle moves along a time-like geodesic.

For 4c, use again

$$
p_\mu=mU_\mu.
$$

Multiplying the lowered geodesic equation by $m$ gives

$$
\frac{dp_\mu}{d\tau}
=
\frac{m}{2}\,\partial_\mu g_{\rho\nu}\,U^\rho U^\nu.
$$

If desired, this may also be written entirely in terms of $p^\mu$ as

$$
\frac{dp_\mu}{d\tau}
=
\frac{1}{2m}\,\partial_\mu g_{\rho\nu}\,p^\rho p^\nu.
$$

Now suppose the metric is independent of $x^1$. Then

$$
\partial_1 g_{\rho\nu}=0.
$$

Setting $\mu=1$ gives

$$
\frac{dp_1}{d\tau}
=
\frac{1}{2m}\,\partial_1 g_{\rho\nu}\,p^\rho p^\nu
=0.
$$

Hence

$$
\boxed{p_1=\text{constant along the geodesic}.}
$$

So any coordinate on which the metric does not depend gives a conserved covariant momentum component, with the time-independent case from 4a corresponding to the conserved quantity $U_0$ (or equivalently $p_0$ up to the constant factor $m$).



### Follow-up Questions

#### 1. Why is the last sentence of 4b not circular, and what does $\nabla_p p$ mean?

The point of the last sentence is not to assume the geodesic equation at the beginning. Rather, the exercise asks you to start from the ordinary flat-space statement that a free massive particle has conserved four-momentum, and then show that this conservation law can be written in a geometric form which is exactly the geodesic equation.

So the intended logic is

$$
\text{free motion in flat spacetime}
\;\Longrightarrow\;
\nabla_p p=0
\;\Longrightarrow\;
\nabla_U U=0,
$$

with

$$
p^\mu=mU^\mu
$$

for a massive particle of constant rest mass $m$.

Thus the question is not assuming geodesic motion first and then restating it. It is asking you to recognise that the usual flat-space law "free particle $\Rightarrow$ constant four-momentum" is the same as the geodesic condition when written covariantly.

Now for the notation. The lecture notes define the covariant derivative in the direction of a vector field $X$ by

$$
(\nabla_X Y)^\mu
=
X^\nu\left(\partial_\nu Y^\mu+\Gamma^\mu_{\rho\nu}Y^\rho\right).
$$

So if we choose $X=Y=p$, then

$$
(\nabla_p p)^\mu
=
p^\nu\nabla_\nu p^\mu
=
p^\nu\left(\partial_\nu p^\mu+\Gamma^\mu_{\rho\nu}p^\rho\right).
$$

Therefore $\nabla_p p$ means the covariant derivative of the momentum vector along itself.

This is directly analogous to

$$
\nabla_U U,
$$

which is the coordinate-free form of the geodesic equation.

Because

$$
p^\mu=mU^\mu
$$

for a massive particle, with constant $m$,

$$
\nabla_p p
=
\nabla_{mU}(mU)
=
m^2\nabla_U U.
$$

Hence

$$
\nabla_p p=0
\qquad\Longleftrightarrow\qquad
\nabla_U U=0.
$$

So $\nabla_p p=0$ is not a different law from the geodesic equation for a massive particle. It is the same condition, written using momentum instead of four-velocity.

In flat inertial coordinates, where $\Gamma^\mu_{\rho\nu}=0$, this becomes

$$
(\nabla_p p)^\mu=p^\nu\partial_\nu p^\mu,
$$

which along the particle's worldline is just the statement that the components of $p^\mu$ stay constant for free motion.

#### 2. How do we get the lowered-index geodesic equation for $U_\mu$? Is it derived from the contravariant one?

Yes. The cleanest way is to start from the contravariant geodesic equation

$$
\frac{D U^\mu}{D\tau}=0
$$

and then lower the index. This works because the metric is covariantly constant, so lowering an index commutes with covariant differentiation.

Start from

$$
U_\mu=g_{\mu\nu}U^\nu.
$$

Take the covariant derivative along the worldline:

$$
\frac{D U_\mu}{D\tau}
=
\frac{D}{D\tau}\left(g_{\mu\nu}U^\nu\right).
$$

Now use the Leibniz rule:

$$
\frac{D U_\mu}{D\tau}
=
\frac{D g_{\mu\nu}}{D\tau}U^\nu
+g_{\mu\nu}\frac{D U^\nu}{D\tau}.
$$

The second term vanishes because the contravariant geodesic equation says

$$
\frac{D U^\nu}{D\tau}=0.
$$

The first term vanishes because metric compatibility gives

$$
g_{\mu\nu;\lambda}=0,
$$

so along the curve

$$
\frac{D g_{\mu\nu}}{D\tau}
=
U^\lambda\nabla_\lambda g_{\mu\nu}
=0.
$$

Therefore

$$
\boxed{\frac{D U_\mu}{D\tau}=0.}
$$

So yes: the lowered-index version is derived directly from the contravariant one by lowering the index after taking the covariant derivative, which is allowed because $\nabla g=0$.

To get the explicit formula, now use the general covariant-derivative rule for a covector $V_\lambda$:

$$
V_{\lambda;\mu}
=
\partial_\mu V_\lambda-\Gamma^\nu_{\mu\lambda}V_\nu.
$$

Along a path this becomes

$$
\frac{D V_\lambda}{D\tau}
=
\frac{dx^\mu}{d\tau}V_{\lambda;\mu}
=
\frac{dV_\lambda}{d\tau}-\Gamma^\nu_{\mu\lambda}\frac{dx^\mu}{d\tau}V_\nu.
$$

Now set

$$
V_\lambda=U_\lambda,
\qquad
\frac{dx^\mu}{d\tau}=U^\mu.
$$

Then

$$
\frac{D U_\lambda}{D\tau}
=
\frac{dU_\lambda}{d\tau}-\Gamma^\nu_{\mu\lambda}U^\mu U_\nu.
$$

Rename the dummy indices $\lambda\to\mu$ and $\nu\to\rho$:

$$
\frac{D U_\mu}{D\tau}
=
\frac{dU_\mu}{d\tau}-\Gamma^\rho_{\nu\mu}U^\nu U_\rho.
$$

Finally, because the Levi-Civita connection is symmetric in its lower indices,

$$
\Gamma^\rho_{\nu\mu}=\Gamma^\rho_{\mu\nu},
$$

so

$$
\boxed{
\frac{D U_\mu}{D\tau}
=
\frac{dU_\mu}{d\tau}-\Gamma^\rho_{\mu\nu}U_\rho U^\nu
=0.
}
$$

That minus sign is the characteristic sign for the covariant derivative of a covector. Contravariant vectors pick up a plus sign, while covectors pick up a minus sign.

So the logic is:

$$
\frac{D U^\mu}{D\tau}=0
\quad\Longrightarrow\quad
\frac{D U_\mu}{D\tau}=0
\quad\Longrightarrow\quad
\frac{dU_\mu}{d\tau}-\Gamma^\rho_{\mu\nu}U_\rho U^\nu=0.
$$



#### 3. How is $V_{\lambda;\mu}=\partial_\mu V_\lambda-\Gamma^\nu_{\mu\lambda}V_\nu$ derived, and how are the rank-two tensor formulas obtained?

Yes. The covariant derivative of a covector is derived from the contravariant-vector rule, but not by naively lowering an index inside the partial derivative. The clean way is to use the fact that the contraction of a vector with a covector is a scalar.

Start from a vector $A^\lambda$ and a covector $V_\lambda$. Their contraction

$$
A^\lambda V_\lambda
$$

is a scalar, so its covariant derivative is just its ordinary derivative:

$$
\nabla_\mu(A^\lambda V_\lambda)
=
\partial_\mu(A^\lambda V_\lambda).
$$

Now apply the Leibniz rule:

$$
\nabla_\mu(A^\lambda V_\lambda)
=
(\nabla_\mu A^\lambda)V_\lambda
+A^\lambda(\nabla_\mu V_\lambda).
$$

For the vector $A^\lambda$ we already know

$$
\nabla_\mu A^\lambda
=
\partial_\mu A^\lambda+\Gamma^\lambda_{\mu\nu}A^\nu.
$$

Therefore

$$
\partial_\mu(A^\lambda V_\lambda)
=
\left(\partial_\mu A^\lambda+\Gamma^\lambda_{\mu\nu}A^\nu\right)V_\lambda
+A^\lambda(\nabla_\mu V_\lambda).
$$

Expand the ordinary derivative on the left:

$$
\partial_\mu A^\lambda\,V_\lambda
+A^\lambda\partial_\mu V_\lambda
=
\partial_\mu A^\lambda\,V_\lambda
+\Gamma^\lambda_{\mu\nu}A^\nu V_\lambda
+A^\lambda(\nabla_\mu V_\lambda).
$$

Cancel the common term $\partial_\mu A^\lambda V_\lambda$ from both sides:

$$
A^\lambda\partial_\mu V_\lambda
=
\Gamma^\lambda_{\mu\nu}A^\nu V_\lambda
+A^\lambda(\nabla_\mu V_\lambda).
$$

Now relabel dummy indices $\lambda\leftrightarrow\nu$ in the connection term:

$$
\Gamma^\lambda_{\mu\nu}A^\nu V_\lambda
=
A^\lambda\Gamma^\nu_{\mu\lambda}V_\nu.
$$

So

$$
A^\lambda\partial_\mu V_\lambda
=
A^\lambda\Gamma^\nu_{\mu\lambda}V_\nu
+A^\lambda(\nabla_\mu V_\lambda).
$$

Factor out the arbitrary vector $A^\lambda$:

$$
A^\lambda\left(\partial_\mu V_\lambda-\Gamma^\nu_{\mu\lambda}V_\nu-\nabla_\mu V_\lambda\right)=0.
$$

Since $A^\lambda$ is arbitrary, the bracket must vanish:

$$
\boxed{
\nabla_\mu V_\lambda
=
\partial_\mu V_\lambda-\Gamma^\nu_{\mu\lambda}V_\nu.
}
$$

So the minus sign appears because covariant indices transform oppositely to contravariant ones. Up-indices get a $+\Gamma$ term, down-indices get a $-\Gamma$ term.

For rank-two tensors, the idea is the same. A tensor with two indices behaves like a direct product of two vectors or covectors, and the covariant derivative obeys the Leibniz rule. So you differentiate the tensor as if each index were being treated separately.

For a purely contravariant tensor $T^{\lambda\kappa}$, think of it as $A^\lambda V^\kappa$. Then

$$
\nabla_\mu(A^\lambda V^\kappa)
=
(\nabla_\mu A^\lambda)V^\kappa
+A^\lambda(\nabla_\mu V^\kappa).
$$

Using the vector rule on each factor gives

$$
\nabla_\mu T^{\lambda\kappa}
=
\partial_\mu T^{\lambda\kappa}
+\Gamma^\lambda_{\mu\nu}T^{\nu\kappa}
+\Gamma^\kappa_{\mu\nu}T^{\lambda\nu}.
$$

Equivalently, in semicolon notation,

$$
\boxed{
T^{\lambda\kappa}{}_{;\mu}
=
\partial_\mu T^{\lambda\kappa}
+\Gamma^\lambda_{\mu\nu}T^{\nu\kappa}
+\Gamma^\kappa_{\mu\nu}T^{\lambda\nu}.
}
$$

For a purely covariant tensor $T_{\lambda\kappa}$, each lower index contributes a minus-sign connection term:

$$
\boxed{
T_{\lambda\kappa;\mu}
=
\partial_\mu T_{\lambda\kappa}
-\Gamma^\nu_{\mu\lambda}T_{\nu\kappa}
-\Gamma^\nu_{\mu\kappa}T_{\lambda\nu}.
}
$$

For a mixed tensor $T^\lambda{}_\kappa$, the upper index contributes a plus sign and the lower index contributes a minus sign:

$$
\boxed{
T^\lambda{}_{\kappa;\mu}
=
\partial_\mu T^\lambda{}_\kappa
+\Gamma^\lambda_{\mu\nu}T^\nu{}_\kappa
-\Gamma^\nu_{\mu\kappa}T^\lambda{}_\nu.
}
$$

So the rule for any tensor is:

1. Start with the ordinary partial derivative.
2. Add one connection term for each upper index.
3. Subtract one connection term for each lower index.
4. In each term, only the chosen index is acted on; all the other indices are left untouched.

That is exactly the pattern Balbus summarises when he says to "unfreeze" one index at a time and treat it as a vector if it is upstairs or a covector if it is downstairs.
