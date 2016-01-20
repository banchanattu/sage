r""" 
Orlik-Solomon Algebras
"""

#*****************************************************************************
#       Copyright (C) 2015 William Slofstra
#                          Travis Scrimshaw <tscrimsh at umn.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.misc.cachefunc import cached_method
from sage.combinat.free_module import CombinatorialFreeModule
from sage.categories.algebras import Algebras
from sage.rings.arith import binomial
from sage.sets.family import Family

class OrlikSolomonAlgebra(CombinatorialFreeModule):
    r"""
    An Orlik-Solomon algebra.

    Let `R` be a commutative ring. Let `M` be a matroid with ground set
    `X`. Let `C(M)` denote the set of circuits of `M`. Let `E` denote
    the exterior algera over `R` generated by `\{ e_x \mid x \in X \}`.
    The *Orlik-Solomon ideal* `J(M)` is the ideal of `E` generated by

    .. MATH::

        \partial e_S := \sum_{i=1}^t (-1)^{i-1} e_{j_1} \wedge e_{j_2}
        \wedge \cdots \wedge \widehat{e}_{j_i} \wedge \cdots \wedge e_{j_t}

    for all `S = \left\{ j_1 < j_2 < \cdots < j_t \right\} \in C(M)`,
    where `\widehat{e}_{j_i}` means that the term `e_{j_i}` is being
    omitted. (The notation `\partial e_S` is not a coincidence, as
    `\partial e_S` is actually the image of `e_S` under the unique
    derivation `\partial` of `E` which sends all `e_x` to `1`.)

    The *Orlik-Solomon algebra* `A(M)` is the quotient `E / J(M)`. Fix
    some ordering on `X`; then, the NBC sets of `M` (that is, the subsets
    of `X` containing no broken circuit of `M`) form a basis of `A(M)`.
    (Here, a *broken circuit* of `M` is defined to be the result of
    removing the smallest element from a circuit of `M`.)

    INPUT:

    - ``R`` -- the base ring
    - ``M`` -- the defining matroid
    - ``ordering`` -- (optional) an ordering of the ground set

    EXAMPLES:

    We create the Orlik-Solomon algebra of the uniform matroid `U(3, 4)`
    and do some basic computations::

        sage: M = matroids.Uniform(3, 4)
        sage: OS = M.orlik_solomon_algebra(QQ)
        sage: OS.dimension()
        14
        sage: G = OS.algebra_generators()
        sage: M.broken_circuits()
        frozenset({frozenset({1, 2, 3})})
        sage: G[1] * G[2] * G[3]
        OS{0, 2, 3} + OS{0, 1, 2} - OS{0, 1, 3}

    REFERENCES:

    .. [CE01] Raul Cordovil and Gwihen Etienne.
       *A note on the Orlik-Solomon algebra*.
       Europ. J. Combinatorics. **22** (2001). pp. 165-170.
       http://www.math.ist.utl.pt/~rcordov/Ce.pdf

    - :wikipedia:`Arrangement_of_hyperplanes#The_Orlik-Solomon_algebra`
    """
    def __init__(self, R, M, ordering=None):
        """
        Initialize ``self``.

        EXAMPLES::

            sage: M = matroids.Wheel(3)
            sage: OS = M.orlik_solomon_algebra(QQ)
            sage: TestSuite(OS).run()
        """
        if ordering is None:
            ordering = sorted(M.groundset())
        self._M = M
        self._sorting = {x:i for i,x in enumerate(ordering)}

        # set up the dictionary of broken circuits
        self._broken_circuits = dict()
        for c in self._M.circuits():
            L = sorted(c, key=lambda x: self._sorting[x])
            self._broken_circuits[frozenset(L[1:])] = L[0]

        cat = Algebras(R).FiniteDimensional().WithBasis().Graded()
        CombinatorialFreeModule.__init__(self, R, M.no_broken_circuits_sets(ordering),
                                         prefix='OS', bracket='{', category=cat)

    def _repr_term(self, m):
        """
        Return a string representation of the term indexed by `m`.

        EXAMPLES::

            sage: M = matroids.Uniform(3, 4)
            sage: OS = M.orlik_solomon_algebra(QQ)
            sage: OS._repr_term(frozenset([0]))
            'OS{0}'
        """
        return "OS{{{}}}".format(str(list(m))[1:-1])

    def _repr_(self):
        """
        Return a string representation of ``self``.

        EXAMPLES::

            sage: M = matroids.Wheel(3)
            sage: M.orlik_solomon_algebra(QQ)
            Orlik-Solomon algebra of Wheel(3): Regular matroid of rank 3
             on 6 elements with 16 bases
        """
        return "Orlik-Solomon algebra of {}".format(self._M)

    @cached_method
    def one_basis(self):
        """
        Return the index of the basis element corresponding to `1`
        in ``self``.

        EXAMPLES::

            sage: M = matroids.Wheel(3)
            sage: OS = M.orlik_solomon_algebra(QQ)
            sage: OS.one_basis() == frozenset([])
            True
        """
        return frozenset({}) 

    @cached_method
    def algebra_generators(self):
        """
        Return the algebra generators of ``self``.

        EXAMPLES::

            sage: M = matroids.Uniform(3, 2)
            sage: OS = M.orlik_solomon_algebra(QQ)
            sage: OS.algebra_generators()
            Finite family {0: OS{0}, 1: OS{1}}
        """
        return Family(sorted(self._M.groundset()),
                      lambda i: self.monomial(frozenset([i])))

    @cached_method
    def product_on_basis(self, a, b):
        """
        Return the product in ``self`` of the basis elements
        indexed by ``a`` and ``b``.

        EXAMPLES::

            sage: M = matroids.Wheel(3)
            sage: OS = M.orlik_solomon_algebra(QQ)
            sage: G = OS.algebra_generators()
            sage: OS.product_on_basis(frozenset([2]), frozenset([3,4]))
            OS{0, 2, 3} + OS{0, 3, 4} + OS{0, 1, 2} - OS{0, 1, 4}

        ::

            sage: prod(G)
            0
            sage: G[2] * G[4]
            -OS{1, 2} + OS{1, 4}
            sage: G[3] * G[4] * G[2]
            OS{0, 2, 3} + OS{0, 3, 4} + OS{0, 1, 2} - OS{0, 1, 4}
            sage: G[2] * G[3] * G[4]
            OS{0, 2, 3} + OS{0, 3, 4} + OS{0, 1, 2} - OS{0, 1, 4}
            sage: G[3] * G[2] * G[4]
            -OS{0, 2, 3} - OS{0, 3, 4} - OS{0, 1, 2} + OS{0, 1, 4}
        """
        if not a:
            return self.basis()[b]
        if not b:
            return self.basis()[a]
        
        if not a.isdisjoint(b):
            return self.zero()

        R = self.base_ring()
        # since a is disjoint from b, we can just multiply the generator
        if len(a) == 1:
            i = list(a)[0]
            # insert i into nbc, keeping track of sign in coeff
            ns = b.union({i})
            ns_sorted = sorted(ns, key=lambda x: self._sorting[x])
            coeff = (-1)**ns_sorted.index(i)

            # now look for a broken circuit to reduce
            for bc in self._broken_circuits:
                if bc.issubset(ns):
                    multiplicand = []
                    # express ns as a product of bc * multiplicand
                    for j in ns_sorted:
                        if j in bc:
                            coeff *= (-1)**len(multiplicand)
                        else:
                            multiplicand.append(j)

                    # reduce bc, and then return the product
                    r = self._reduce_broken_circuit(bc)
                    return R(coeff) * r * self.monomial(frozenset(multiplicand))

            # if we got this far, return ns
            return self._from_dict({ns: coeff}, remove_zeros=False)

        # r is the accumalator
        # we reverse a in the product, so add a sign
        # note that l>=2 here
        r = self._from_dict({b: R((-1)**binomial(len(a),2))}, remove_zeros=False)

        # now do the multiplication generator by generator
        G = self.algebra_generators()
        for i in sorted(a, key=lambda x: self._sorting[x]):
            r = G[i] * r 

        return r

    @cached_method
    def _reduce_broken_circuit(self, bc):
        """
        Reduce the broken circuit ``bc`` to a sum of terms with
        lower term order in ``self``.

        EXAMPLES::

            sage: M = matroids.Wheel(3)
            sage: OS = M.orlik_solomon_algebra(QQ)
            sage: BC = sorted(M.broken_circuits(), key=sorted)
            sage: for bc in BC: (sorted(bc), OS._reduce_broken_circuit(bc))
            ([1, 3], OS{0, 3} - OS{0, 1})
            ([1, 4, 5], OS{0, 1, 4} - OS{0, 1, 5} + OS{0, 4, 5})
            ([2, 3, 4], OS{0, 2, 3} + OS{0, 3, 4} - OS{0, 2, 4})
            ([2, 3, 5], OS{1, 3, 5} + OS{1, 2, 3} - OS{1, 2, 5})
            ([2, 4], -OS{1, 2} + OS{1, 4})
            ([2, 5], OS{0, 5} - OS{0, 2})
            ([4, 5], -OS{3, 4} + OS{3, 5})
        """
        r = self.zero()
        i = self._broken_circuits[bc]
        c = self.base_ring().one()
        for j in sorted(bc, key=lambda x: self._sorting[x]):
            r += self._from_dict({bc.symmetric_difference({i,j}): c},
                                 remove_zeros=False)
            c *= -1
        return r

    def degree_on_basis(self, m):
        """
        Return the degree of the basis element indexed by ``m``.

        EXAMPLES::

            sage: M = matroids.Wheel(3)
            sage: OS = M.orlik_solomon_algebra(QQ)
            sage: OS.degree_on_basis(frozenset([1]))
            1
            sage: OS.degree_on_basis(frozenset([0, 2, 3]))
            3
        """
        return len(m)

