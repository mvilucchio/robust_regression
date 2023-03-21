from numpy import divide, identity, sqrt, abs, count_nonzero, sum, dot, ones_like, inf, tile, finfo, float64, empty, nonzero
import numpy as np
from numpy.linalg import norm
from numpy.linalg import solve
from numpy.random import normal
from numba import njit, prange
from scipy.optimize import minimize
from cvxpy import Variable, Minimize, Problem, norm, sum_squares
from ..utils.matrix_utils import axis0_pos_neg_mask, safe_sparse_dot
from ..regression_numerics import GTOL_MINIMIZE, MAX_ITER_MINIMIZE, BLEND_GAMP, TOL_GAMP


@njit(error_model="numpy", fastmath=True)
def find_coefficients_L2(ys, xs, reg_param):
    _, d = xs.shape
    a = divide(xs.T.dot(xs), d) + reg_param * identity(d)
    b = divide(xs.T.dot(ys), sqrt(d))
    return solve(a, b)


def find_coefficients_L1(ys, xs, reg_param):
    _, d = xs.shape
    # w = np.random.normal(loc=0.0, scale=1.0, size=(d,))
    xs_norm = divide(xs, sqrt(d))
    w = Variable(shape=d)
    obj = Minimize(norm(ys - xs_norm @ w, 1) + 0.5 * reg_param * sum_squares(w))
    prob = Problem(obj)
    prob.solve(eps_abs=1e-3)
    return w.value


@njit(error_model="numpy")
def _loss_and_gradient_Huber(w, xs_norm, ys, reg_param, a):
    linear_loss = ys - xs_norm @ w
    abs_linear_loss = abs(linear_loss)
    outliers_mask = abs_linear_loss > a

    outliers = abs_linear_loss[outliers_mask]
    num_outliers = count_nonzero(outliers_mask)
    n_non_outliers = xs_norm.shape[0] - num_outliers

    loss = a * sum(outliers) - 0.5 * num_outliers * a**2

    non_outliers = linear_loss[~outliers_mask]
    loss += 0.5 * dot(non_outliers, non_outliers)
    loss += 0.5 * reg_param * dot(w, w)

    (xs_outliers, xs_non_outliers) = axis0_pos_neg_mask(xs_norm, outliers_mask, num_outliers)
    xs_non_outliers *= -1.0

    gradient = safe_sparse_dot(non_outliers, xs_non_outliers)

    signed_outliers = ones_like(outliers)
    signed_outliers_mask = linear_loss[outliers_mask] < 0
    signed_outliers[signed_outliers_mask] = -1.0

    gradient -= a * safe_sparse_dot(signed_outliers, xs_outliers)
    gradient += reg_param * w

    return loss, gradient


def find_coefficients_Huber(ys, xs, reg_param, a):
    _, d = xs.shape
    w = normal(loc=0.0, scale=1.0, size=(d,))
    xs_norm = divide(xs, sqrt(d))

    bounds = tile([-inf, inf], (w.shape[0], 1))
    bounds[-1][0] = finfo(float64).eps * 10

    opt_res = minimize(
        _loss_and_gradient_Huber,
        w,
        method="L-BFGS-B",
        jac=True,
        args=(xs_norm, ys, reg_param, a),
        options={"maxiter": MAX_ITER_MINIMIZE, "gtol": GTOL_MINIMIZE, "iprint": -1},
        bounds=bounds,
    )

    if opt_res.status == 2:
        raise ValueError(
            "HuberRegressor convergence failed: l-BFGS-b solver terminated with %s"
            % opt_res.message
        )

    return opt_res.x


def find_coefficients_Huber_on_sphere(ys, xs, reg_param, q_fixed, a, gamma = 1e-04):
    _, d = xs.shape
    w = normal(loc=0.0, scale=1.0, size=(d,)) / sqrt(norm(w)) * sqrt(q_fixed)
    xs_norm = divide(xs, sqrt(d))

    loss, grad = _loss_and_gradient_Huber(w, xs_norm, ys, reg_param, a)
    iter = 0
    while iter < MAX_ITER_MINIMIZE and norm(grad) > GTOL_MINIMIZE:
        if iter % 10 == 0:
            print(str(iter) + 'th Iteration    Loss :: ' + str(loss) + ' gradient :: ' +  str(norm(grad)))

        alpha = 1
        new_w = w - alpha * grad
        new_loss, new_grad = _loss_and_gradient_Huber(w, xs_norm, ys, reg_param, a)

        while new_loss > loss - gamma * alpha * norm(grad):
            alpha = alpha / 2
            new_w = w - alpha * grad
            new_loss, new_grad = _loss_and_gradient_Huber(w, xs_norm, ys, reg_param, a)

        loss = new_loss
        grad = new_grad
        w = new_w

        iter += 1

    return w