from numpy import logspace, empty
from math import log10
from typing import Tuple
from ..fixed_point_equations.fpeqs import fixed_point_finder
from ..aux_functions.misc import gen_error
from ..fixed_point_equations import SMALLEST_REG_PARAM, SMALLEST_HUBER_PARAM
from ..fixed_point_equations.optimality_finding import (
    find_optimal_reg_param_function,
    find_optimal_reg_and_huber_parameter_function,
)


def sweep_eps_fixed_point(
    var_func,
    var_hat_func,
    eps_min: float,
    eps_max: float,
    n_eps_pts: int,
    var_func_kwargs: dict,
    var_hat_func_kwargs: dict,
    initial_cond=(0.6, 0.01, 0.9),
    funs=[gen_error],
    funs_args=[list()],
    decreasing=False,
):
    if len(funs) != len(funs_args):
        raise ValueError(
            "The length of funs and funs_args should be the same, in this case is {:d} and {:d}".format(
                len(funs), len(funs_args)
            )
        )

    if eps_min > eps_max:
        raise ValueError(
            "eps_min should be smaller than eps_max, in this case are {:f} and {:f}".format(
                eps_min, eps_max
            )
        )

    if eps_min < 0:
        raise ValueError(
            "eps_min should be positive or equal to zero, in this case is {:f}".format(eps_min)
        )

    n_observables = len(funs)
    epsilons = (
        logspace(log10(eps_min), log10(eps_max), n_eps_pts)
        if not decreasing
        else logspace(log10(eps_max), log10(eps_min), n_eps_pts)
    )
    out_list = [empty(n_eps_pts) for _ in range(n_observables)]

    copy_var_hat_func_kwargs = var_hat_func_kwargs.copy()

    old_initial_cond = initial_cond
    for idx, eps in enumerate(epsilons):
        copy_var_hat_func_kwargs.update({"percentage": eps})

        m, q, sigma = fixed_point_finder(
            var_func, var_hat_func, old_initial_cond, var_func_kwargs, copy_var_hat_func_kwargs
        )

        old_initial_cond = tuple([m, q, sigma])

        for jdx, (f, f_args) in enumerate(zip(funs, funs_args)):
            out_list[jdx][idx] = f(m, q, sigma, *f_args)

    if decreasing:
        epsilons = epsilons[::-1]
        for idx, obs_vals in enumerate(out_list):
            out_list[idx] = obs_vals[::-1]

    return epsilons, out_list


def sweep_eps_optimal_lambda_fixed_point(
    var_func,
    var_hat_func,
    eps_min: float,
    eps_max: float,
    n_eps_pts: int,
    inital_guess_lambda: float,
    var_func_kwargs: dict,
    var_hat_func_kwargs: dict,
    initial_cond_fpe=(0.6, 0.01, 0.9),
    funs=[gen_error],
    funs_args=[list()],
    f_min=gen_error,
    f_min_args=(),
    min_reg_param=SMALLEST_REG_PARAM,
    decreasing=False,
):
    if len(funs) != len(funs_args):
        raise ValueError(
            "The length of funs and funs_args should be the same, in this case is {:d} and {:d}".format(
                len(funs), len(funs_args)
            )
        )

    if eps_min > eps_max:
        raise ValueError(
            "eps_min should be smaller than eps_max, in this case are {:f} and {:f}".format(
                eps_min, eps_max
            )
        )

    n_observables = len(funs)
    epsilons = (
        logspace(log10(eps_min), log10(eps_max), n_eps_pts)
        if not decreasing
        else logspace(log10(eps_max), log10(eps_min), n_eps_pts)
    )
    f_min_vals = empty(n_eps_pts)
    reg_params_opt = empty(n_eps_pts)
    funs_values = [empty(n_eps_pts) for _ in range(n_observables)]

    copy_var_func_kwargs = var_func_kwargs.copy()
    copy_var_hat_func_kwargs = var_hat_func_kwargs.copy()

    old_initial_cond_fpe = initial_cond_fpe
    old_reg_param_opt = inital_guess_lambda
    for idx, eps in enumerate(epsilons):
        copy_var_hat_func_kwargs.update({"percentage": eps})
        copy_var_func_kwargs.update({"reg_param": old_reg_param_opt})

        (
            f_min_vals[idx],
            reg_params_opt[idx],
            (m, q, sigma),
            out_values,
        ) = find_optimal_reg_param_function(
            var_func,
            var_hat_func,
            copy_var_func_kwargs,
            copy_var_hat_func_kwargs,
            old_reg_param_opt,
            old_initial_cond_fpe,
            funs=funs,
            funs_args=funs_args,
            f_min=f_min,
            f_min_args=f_min_args,
            min_reg_param=min_reg_param,
        )
        old_reg_param_opt = reg_params_opt[idx]
        old_initial_cond_fpe = (m, q, sigma)

        for jdx in range(n_observables):
            funs_values[jdx][idx] = out_values[jdx]

    # change this
    if decreasing:
        epsilons = epsilons[::-1]
        f_min_vals = f_min_vals[::-1]
        reg_params_opt = reg_params_opt[::-1]
        for idx, fun_vals in enumerate(funs_values):
            funs_values[idx] = fun_vals[::-1]

    return epsilons, f_min_vals, reg_params_opt, funs_values


def sweep_eps_optimal_lambda_hub_param_fixed_point(
    var_func,
    var_hat_func,
    eps_min: float,
    eps_max: float,
    n_eps_pts: int,
    inital_guess_params: Tuple[float, float],
    var_func_kwargs: dict,
    var_hat_func_kwargs: dict,
    initial_cond_fpe=(0.6, 0.01, 0.9),
    funs=[gen_error],
    funs_args=[list()],
    f_min=gen_error,
    f_min_args=(),
    min_reg_param=SMALLEST_REG_PARAM,
    min_huber_param=SMALLEST_HUBER_PARAM,
    decreasing=False,
):
    if len(funs) != len(funs_args):
        raise ValueError(
            "The length of funs and funs_args should be the same, in this case is {:d} and {:d}".format(
                len(funs), len(funs_args)
            )
        )

    if eps_min > eps_max:
        raise ValueError(
            "eps_min should be smaller than eps_max, in this case are {:f} and {:f}".format(
                eps_min, eps_max
            )
        )

    n_observables = len(funs)
    epsilons = (
        logspace(log10(eps_min), log10(eps_max), n_eps_pts)
        if not decreasing
        else logspace(log10(eps_max), log10(eps_min), n_eps_pts)
    )
    f_min_vals = empty(n_eps_pts)
    reg_params_opt = empty(n_eps_pts)
    hub_params_opt = empty(n_eps_pts)
    funs_values = [empty(n_eps_pts) for _ in range(n_observables)]

    copy_var_func_kwargs = var_func_kwargs.copy()
    copy_var_hat_func_kwargs = var_hat_func_kwargs.copy()

    old_initial_cond_fpe = initial_cond_fpe
    old_reg_param_opt = inital_guess_params[0]
    old_hub_param_opt = inital_guess_params[1]
    for idx, eps in enumerate(epsilons):
        copy_var_hat_func_kwargs.update({"percentage": eps, "a": old_hub_param_opt})
        copy_var_func_kwargs.update({"reg_param": old_reg_param_opt})

        (
            f_min_vals[idx],
            (reg_params_opt[idx], hub_params_opt[idx]),
            (m, q, sigma),
            out_values,
        ) = find_optimal_reg_and_huber_parameter_function(
            var_func,
            var_hat_func,
            copy_var_func_kwargs,
            copy_var_hat_func_kwargs,
            (old_reg_param_opt, old_hub_param_opt),
            old_initial_cond_fpe,
            funs=funs,
            funs_args=funs_args,
            f_min=f_min,
            f_min_args=f_min_args,
            min_reg_param=min_reg_param,
            min_huber_param=min_huber_param,
        )

        old_reg_param_opt = reg_params_opt[idx]
        old_hub_param_opt = hub_params_opt[idx]
        old_initial_cond_fpe = (m, q, sigma)

        for jdx in range(n_observables):
            funs_values[jdx][idx] = out_values[jdx]

    #  to be checked
    if decreasing:
        epsilons = epsilons[::-1]
        f_min_vals = f_min_vals[::-1]
        reg_params_opt = reg_params_opt[::-1]
        hub_params_opt = hub_params_opt[::-1]
        for idx, fun_vals in enumerate(funs_values):
            funs_values[idx] = fun_vals[::-1]

    return epsilons, f_min_vals, (reg_params_opt, hub_params_opt), funs_values
