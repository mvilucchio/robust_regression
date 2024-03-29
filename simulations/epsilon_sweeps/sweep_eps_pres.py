import robust_regression.sweeps.eps_sweep as epsw
import matplotlib.pyplot as plt
from robust_regression.fixed_point_equations.fpe_L2_regularization import var_func_L2
from robust_regression.fixed_point_equations.fpe_L2_loss import (
    var_hat_func_L2_decorrelated_noise,
)
from robust_regression.fixed_point_equations.fpe_L1_loss import (
    var_hat_func_L1_decorrelated_noise,
)
from robust_regression.fixed_point_equations.fpe_Huber_loss import (
    var_hat_func_Huber_decorrelated_noise,
)
import numpy as np
from robust_regression.aux_functions.stability_functions import (
    stability_ridge,
    stability_l1_l2,
    stability_huber,
)

def sigma_order_param(m, q, sigma):
    return sigma

def q_order_param(m, q, sigma):
    return q

def m_order_param(m, q, sigma):
    return m

alpha, delta_in, delta_out, beta = 10.0, 0.1, 5.0, 0.0
eps_min, eps_max, n_eps_pts = 0.01, 0.75, 750

while True:
    m = 0.89 * np.random.random() + 0.1
    q = 0.89 * np.random.random() + 0.1
    sigma = 0.89 * np.random.random() + 0.1
    if np.square(m) < q + delta_in * q and np.square(m) < q + delta_out * q:
        initial_condition = [m, q, sigma]
        break

epsilons, e_gen_l2, reg_params_opt_l2, (ms_l2, qs_l2, sigmas_l2) = epsw.sweep_eps_optimal_lambda_fixed_point(
    var_func_L2,
    var_hat_func_L2_decorrelated_noise,
    eps_min, eps_max, n_eps_pts,
    0.1,
    {"reg_param": 3.0},
    {
        "alpha": alpha,
        "delta_in": delta_in,
        "delta_out": delta_out,
        "percentage": 0.3,
        "beta": beta,
    },
    initial_cond_fpe=initial_condition,
    funs=[m_order_param, q_order_param, sigma_order_param],
    funs_args=[list(), list(), list()],
)

print("L2 done")

_, e_gen_l1, reg_params_opt_l1, (ms_l1, qs_l1, sigmas_l1) = epsw.sweep_eps_optimal_lambda_fixed_point(
    var_func_L2,
    var_hat_func_L1_decorrelated_noise,
    eps_min, eps_max, n_eps_pts,
    0.5,
    {"reg_param": 3.0},
    {
        "alpha": alpha,
        "delta_in": delta_in,
        "delta_out": delta_out,
        "percentage": 0.3,
        "beta": beta,
    },
    initial_cond_fpe=initial_condition,
    funs=[m_order_param, q_order_param, sigma_order_param],
    funs_args=[list(), list(), list()],
)

print("L1 done")

_, e_gen_hub, (reg_params_opt_hub, hub_params_opt), (ms_hub, qs_hub, sigmas_hub) = epsw.sweep_eps_optimal_lambda_hub_param_fixed_point(
    var_func_L2,
    var_hat_func_Huber_decorrelated_noise,
    eps_min, eps_max, n_eps_pts,
    [0.5, 1.0],
    {"reg_param": 3.0},
    {
        "alpha": alpha,
        "delta_in": delta_in,
        "delta_out": delta_out,
        "percentage": 0.3,
        "beta": beta,
        "a": 1.0,
    },
    initial_cond_fpe=initial_condition,
    funs=[m_order_param, q_order_param, sigma_order_param],
    funs_args=[list(), list(), list()],
)

print("Huber done")

stabs_l2 = stability_ridge(ms_l2, qs_l2, sigmas_l2, alpha, reg_params_opt_l2, delta_in, delta_out, epsilons, beta)
stabs_l1 = stability_l1_l2(ms_l1, qs_l1, sigmas_l1, alpha, reg_params_opt_l1, delta_in, delta_out, epsilons, beta)
stabs_hub = stability_huber(ms_hub, qs_hub, sigmas_hub, alpha, reg_params_opt_hub, delta_in, delta_out, epsilons, beta, hub_params_opt)

# ----------------------------

plt.figure(figsize=(10, 10))

plt.subplot(311)
plt.plot(epsilons, e_gen_l2, label="L2")
plt.plot(epsilons, e_gen_l1, label="L1")
plt.plot(epsilons, e_gen_hub, label="Huber")
plt.xlabel(r"$\epsilon$")
plt.ylabel(r"$E_{gen}$")
plt.xscale("log")
plt.yscale("log")
plt.grid()

plt.subplot(312)
plt.plot(epsilons, reg_params_opt_l2, label="L2")
plt.plot(epsilons, reg_params_opt_l1, label="L1")
plt.plot(epsilons, reg_params_opt_hub, label="Huber")
plt.xlabel(r"$\epsilon$")
plt.ylabel(r"$\lambda_{opt}$")
plt.xscale("log")
plt.grid()

plt.subplot(313)
plt.plot(epsilons, stabs_l2, label="L2")
plt.plot(epsilons, stabs_l1, label="L1")
plt.plot(epsilons, stabs_hub, label="Huber")
plt.xlabel(r"$\epsilon$")
plt.ylabel(r"Stability cond.")
plt.xscale("log")
plt.grid()

plt.show()