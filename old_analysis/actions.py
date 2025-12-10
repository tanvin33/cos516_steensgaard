"""
Code for unification logic and constraint generation as per Steensgaard's analysis.
"""

from type import Type


####################
# Unification logic
####################
def unify_alpha(manager, a, b):
    uf = manager.uf

    a_id = uf.find(a.uf_id)
    b_id = uf.find(b.uf_id)

    # Check if already unified
    if a_id == b_id:
        return

    # Union in UF
    uf.union(a_id, b_id)

    # Resolve unified type
    u_id = uf.find(a_id)
    u = manager.nodes[u_id]

    a_u = manager.nodes[a_id]
    b_u = manager.nodes[b_id]

    unify_tau(manager, a_u, b_u, u)
    unify_lambda(manager, a_u, b_u, u)


def unify_tau(manager, a, b, u):
    a_ref = a.tau_ref
    b_ref = b.tau_ref

    if a_ref is None and b_ref is None:
        return
    if a_ref is None:
        u.tau_ref = b_ref
        return
    if b_ref is None:
        u.tau_ref = a_ref
        return

    # If neither are bottom, choose one
    u.tau_ref = a_ref
    unify_alpha(manager, a_ref, b_ref)


def unify_lambda(manager, a, b, u):
    a_args = a.lam_args
    b_args = b.lam_args
    a_rets = a.lam_rets
    b_rets = b.lam_rets

    if a_args is None and b_args is None:
        return
    if a_args is None:
        u.lam_args = b_args
        u.lam_rets = b_rets
        return
    if b_args is None:
        u.lam_args = a_args
        u.lam_rets = a_rets
        return

    # If neither are bottom, choose one
    u.lam_args = a_args
    u.lam_rets = a_rets

    # assert len(a_args) == len(b_args)
    # assert len(a_rets) == len(b_rets)

    for i, a_u in enumerate(a_args):
        b_u = b_args[i]
        unify_alpha(manager, a_u, b_u)

    for i, a_u in enumerate(a_rets):
        b_u = b_rets[i]
        unify_alpha(manager, a_u, b_u)


########################
# Constraint generation
########################
def constraint_assign(manager, x, y):
    # x = y
    unify_alpha(manager, x, y)


def constraint_addr_of(manager, x, y):
    # x = &y
    if x.tau_ref is None:
        x.tau_ref = y
    else:
        unify_alpha(manager, x.tau_ref, y)


def constraint_deref(manager, x, y):
    # x = *y
    if y.tau_ref is None:
        # TODO: check if this is right
        y.tau_ref = manager.new_alpha(x.uf_id)

    unify_alpha(manager, x, y.tau_ref)


def constraint_store(manager, x, y):
    # *x = y
    if x.tau_ref is None:
        # TODO: check if this is right

        x.tau_ref = manager.new_alpha(y.uf_id)

    unify_alpha(manager, x.tau_ref, y)
