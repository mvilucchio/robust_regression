import robust_regression.sweeps.alpha_sweeps as alsw
import matplotlib.pyplot as plt
from scipy.special import erf
from robust_regression.fixed_point_equations.fpe_L2_regularization import var_func_L2
from robust_regression.fixed_point_equations.fpe_L2_loss import (
    var_hat_func_L2_decorrelated_noise,
    order_parameters_ridge,
)
from robust_regression.fixed_point_equations.fpe_L1_loss import (
    var_hat_func_L1_decorrelated_noise,
)
from robust_regression.fixed_point_equations.fpe_Huber_loss import (
    var_hat_func_Huber_decorrelated_noise,
)
import numpy as np


def m_order_param(m, q, sigma):
    return m


def q_order_param(m, q, sigma):
    return q


def sigma_order_param(m, q, sigma):
    return sigma


delta_in, delta_out, percentage, beta = 1.0, 5.0, 0.3, 0.0


# alphas, f_min_vals, (reg_param_opt, hub_param_opt), (sigmas,) = alsw.sweep_alpha_optimal_lambda_hub_param_fixed_point(
#     var_func_L2,
#     var_hat_func_Huber_decorrelated_noise,
#     0.1,
#     100,
#     250,
#     [1.0, 1.0],
#     {"reg_param": 3.0},
#     {
#         "delta_in": delta_in,
#         "delta_out": delta_out,
#         "percentage": percentage,
#         "beta": beta,
#         "a": 1.0
#     },
#     initial_cond_fpe=(0.6, 0.2, 0.9),
#     funs=[sigma_order_param],
#     funs_args=[{}],
# )

n_features = 700
repetitions = 10

alphas = list()
gen_error_mean_hub = list()
gen_error_std_hub = list()
gen_error_mean_l1 = list()
gen_error_std_l1 = list()
gen_error_mean_l2 = list()
gen_error_std_l2 = list()

# data = np.genfromtxt(
#     "./data/TEST_alpha_sweep_L2.csv",
#     delimiter=',',
#     skip_header=1
# )
# alphas_prev = data[:,0]
# err_prev_l2 = data[:,1]
# lambda_prev_l2 = data[:,2]


# n_points = 1000
# reg_params = np.linspace(1, -5, n_points)

# sigmas = np.empty(len(alphas_prev))
# for idx, (alpha, rp) in enumerate(zip(alphas_prev, lambda_prev_l2)):
#     _, _, sigmas[idx], _, _, _ = order_parameters_ridge(alpha, rp, delta_in, delta_out, percentage, beta, 1.0)

alphas, f_min_vals, reg_param_opt, (ms, qs, sigmas,) = alsw.sweep_alpha_optimal_lambda_fixed_point(
    var_func_L2,
    var_hat_func_L2_decorrelated_noise,
    1000,
    1000000,
    100,
    3.0,
    {"reg_param": 3.0},
    {
        "delta_in": delta_in,
        "delta_out": delta_out,
        "percentage": percentage,
        "beta": beta,
    },
    initial_cond_fpe=(0.6, 0.01, 0.9),
    funs=[m_order_param, q_order_param, sigma_order_param],
    funs_args=[{}, {}, {}],
)

first_idx = 0
for idx, rp in enumerate(reg_param_opt):
    if rp <= 0.0:
        first_idx = idx
        break

plt.figure(figsize=(6, 6))

import numpy as np
import matplotlib.pyplot as plt


# Convert the data to log-log scale
x_log = np.log10(alphas)
y_log = np.log10(np.abs(reg_param_opt))

# Fit a straight line to the data in log-log scale
coefficients = np.polyfit(x_log, y_log, 1)
slope = coefficients[0]
intercept = coefficients[1]

# Plot the data and the fitted line
print(slope, intercept)


plt.subplot(2, 1, 1)
plt.title(
    "L2 loss, L2 reg, $\\alpha$ sweep, $\\Delta_{{in}} = {}$, $\\Delta_{{out}} = {}$, $\\epsilon = {}$, $\\beta = {}$".format(
        delta_in, delta_out, percentage, beta
    )
)
plt.plot(alphas, np.abs(reg_param_opt), label="$\\|\\lambda_{{opt}}\\|$")
plt.plot(
    alphas,
    np.abs(
        alphas
        * percentage
        / (sigmas + 1)
    ),
    label="$\\alpha \\epsilon Z_{{out}}$",
)
plt.axvline(alphas[first_idx], color="red")
plt.xscale("log")
# plt.ylim([-10,8])
plt.ylabel(r"$\lambda_{opt}$")
plt.legend()
plt.yscale("log")
plt.xlabel("$\\alpha$")
plt.grid()


alphas_c, _, reg_param_opt_c, (ms_c, qs_c, sigmas_c,) = alsw.sweep_alpha_optimal_lambda_fixed_point(
    var_func_L2,
    var_hat_func_L2_decorrelated_noise,
    1,
    10000,
    100,
    3.0,
    {"reg_param": 3.0},
    {
        "delta_in": delta_in,
        "delta_out": delta_out,
        "percentage": percentage,
        "beta": 1.0,
    },
    initial_cond_fpe=(0.6, 0.01, 0.9),
    funs=[m_order_param, q_order_param, sigma_order_param],
    funs_args=[{}, {}, {}],
)

alphas_cc, _, reg_param_opt_cc, (ms_cc, qs_cc, sigmas_cc,) = alsw.sweep_alpha_optimal_lambda_fixed_point(
    var_func_L2,
    var_hat_func_L2_decorrelated_noise,
    1,
    10000,
    100,
    3.0,
    {"reg_param": 3.0},
    {
        "delta_in": delta_in,
        "delta_out": delta_out,
        "percentage": percentage,
        "beta": 1.0,
    },
    initial_cond_fpe=(0.6, 0.01, 0.9),
    funs=[m_order_param, q_order_param, sigma_order_param],
    funs_args=[{}, {}, {}],
)

plt.subplot(2, 1, 2)
plt.plot(
    alphas,
    reg_param_opt + (
        alphas
        * percentage
        / (sigmas+1)
    ),
    label="$\\lambda_{{opt}} + \\alpha \\epsilon Z_{{out}}$",
)

plt.plot(alphas_c, reg_param_opt_c, label="1")
plt.plot(alphas_c, percentage * reg_param_opt_c, label="2")
plt.plot(alphas_c, (1 - percentage) * reg_param_opt_c, label="3")

plt.xscale("log")
plt.legend()
plt.xlabel("$\\alpha$")
plt.grid()

plt.show()