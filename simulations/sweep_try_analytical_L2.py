import robust_regression.sweeps.alpha_sweeps as alsw
import matplotlib.pyplot as plt
from robust_regression.fixed_point_equations.fpe_L2_loss import (
    var_func_L2,
    var_hat_func_L2_decorrelated_noise,
    order_parameters_ridge
)
from robust_regression.fixed_point_equations.fpe_L1_loss import (
    var_func_L2,
    var_hat_func_L1_decorrelated_noise,
)
from robust_regression.fixed_point_equations.fpe_Huber_loss import (
    var_func_L2,
    var_hat_func_Huber_decorrelated_noise,
)
import numpy as np


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

data = np.genfromtxt(
    "./data/TEST_alpha_sweep_L2.csv",
    delimiter=',',
    skip_header=1
)
alphas_prev = data[:,0]
err_prev_l2 = data[:,1]
lambda_prev_l2 = data[:,2]


# n_points = 1000
# reg_params = np.linspace(1, -5, n_points)

sigmas = np.empty(len(alphas_prev))
for idx, (alpha, rp) in enumerate(zip(alphas_prev, lambda_prev_l2)):
    _, _, sigmas[idx], _, _, _ = order_parameters_ridge(alpha, rp, delta_in, delta_out, percentage, beta, 1.0)

alphas, f_min_vals, reg_param_opt, (sigmas,) = alsw.sweep_alpha_optimal_lambda_fixed_point(
    var_func_L2,
    var_hat_func_L2_decorrelated_noise,
    0.01,
    100,
    200,
    3.0,
    {"reg_param": 3.0},
    {
        "delta_in": delta_in,
        "delta_out": delta_out,
        "percentage": percentage,
        "beta": beta,
    },
    initial_cond_fpe=(0.6, 0.01, 0.9),
    funs=[sigma_order_param],
    funs_args=[{}],
)

first_idx = 0
for idx, rp in enumerate(reg_param_opt):
    if rp <= 0.0:
        first_idx = idx
        break

def condition_MP(alphas):
    return np.minimum(0.0, (1 - alphas))

plt.figure(figsize=(10, 10))

plt.subplot(311)
plt.title("Ridge regression, L2 loss, L2 noise, $\\alpha$ sweep, $\\delta_{{in}} = {}$, $\\delta_{{out}} = {}$, $\\beta = {}$".format(delta_in, delta_out, beta))
plt.plot(alphas, f_min_vals)
plt.yscale("log")
plt.xscale("log")
plt.ylabel(r"$E_{gen}$")
plt.grid()

plt.subplot(312)
plt.plot(alphas, reg_param_opt, label=r"$\lambda_{opt}$")
# plt.plot(alphas, hub_param_opt, label=r"$\alpha_{opt}$")
plt.plot(alphas, condition_MP(alphas), label=r"$min (0, 1-\alpha) $")
plt.axvline(alphas[first_idx], color="red")
plt.xscale("log")
plt.ylim([-30,8])
plt.ylabel(r"$\lambda_{opt}$")
plt.legend()
plt.grid()

plt.subplot(313)
plt.plot(alphas, 1 - alphas * (sigmas / (sigmas + 1))**2)
plt.axvline(alphas[first_idx], color="red")
plt.xscale("log")
plt.grid()
plt.ylabel(r"$1 - \alpha \Sigma^2 / (\Sigma + 1)^2$")
plt.xlabel(r"$\alpha$")

plt.show()

# np.savetxt(
#     "./data/TEST_alpha_sweep_L1.csv",
#     np.array([alphas, f_min_vals, reg_param_opt]).T,
#     delimiter=",",
#     header="alpha, f_min, lambda_opt",
# )