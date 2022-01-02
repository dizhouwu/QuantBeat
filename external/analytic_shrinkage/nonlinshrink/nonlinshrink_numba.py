import numpy as np
from numba import njit
import sys
import os

from nonlinshrink.nls_exceptions import (
    InputDimensionException,
    SampleSizeException,
)

EPS = 1e-8


@njit
def np_apply_along_axis(func1d, axis, arr):
    if not arr.ndim == 2:
        raise InputDimensionException("Input must be a 2d array")
    if axis not in {0, 1}:
        raise ValueError("axis must be 0 or 1")
    if axis == 0:
        result = np.empty(arr.shape[1])
        for i in range(len(result)):
            result[i] = func1d(arr[:, i])
    else:
        result = np.empty(arr.shape[0])
        for i in range(len(result)):
            result[i] = func1d(arr[i, :])
    return result


@njit
def np_mean(array, axis):
    return np_apply_along_axis(np.mean, axis, array)


@njit
def np_std(array, axis):
    return np_apply_along_axis(np.std, axis, array)


@njit
def shrink_cov(data, k=None):
    """Shrink covarince matrix using non-linear shrinkage as described in
    Ledoit and Wolf 2018 http://www.econ.uzh.ch/static/wp/econwp264.pdf .
    The code uses an analytic formula which was previously not available
    and is thus much faster because there is no optimization necessary. The code can
    also handle the high-dimensional setting with p>n .

    Args:
        data (`numpy.ndarray`): Data matrix with each observation in rows of the matrix,
            i.e. an n-by-p matrix with n observations and p dimensional variables.
        k (int, optional): If this parameter k is None,
             the algorithm demeans the data by default, and then adjusts
             the effective sample size accordingly by subtracting one.
            If the user inputs k = 0, then no demeaning takes place and
             the effective sample size remains n.
             If the user inputs k >= 1, then it signifies that the data X
             has already been demeaned or otherwise pre-processed; for example,
             the data might constitute OLS residuals based on a linear regression
             model with k regressors. No further demeaning takes place then,
             but the effective sample size is adjusted accordingly by subtracting k.

    Returns:
        `numpy.ndarray`: Shrunk covariance matrix
    """
    shape = data.shape
    if len(data.shape) != 2:
        raise InputDimensionException("Input must be a 2d array")
    n, p = shape
    if k is None:
        data = data - np_mean(data, 0)
        k = 1

    n = n - k  # effective sample size
    if n < 12:
        raise SampleSizeException("Sample size n must be >= 12")

    sample_cov = np.dot(data.T, data) / n

    # % extract sample eigenvalues sorted in ascending order and eigenvectors
    lam, u = np.linalg.eigh(sample_cov)
    # compute analytical nonlinear shrinkage kernel formula
    lam = lam[np.maximum(0, p - n) :]
    for _ in lam:
        if _ / sum(lam) < EPS:
            raise ValueError("Matrix is singular")
    L = lam.T.repeat(np.minimum(p, n)).reshape(-1, np.minimum(p, n))
    h = np.power(n, -1 / 3.0)
    # % Equation(4.9)
    H = h * L.T
    x = (L - L.T) / H
    ftilde = (3 / 4.0 / np.sqrt(5)) * np_mean(np.maximum(1 - x ** 2.0 / 5.0, 0) / H, 1)
    # % Equation(4.7)
    Hftemp = (-3 / 10 / np.pi) * x + (3 / 4.0 / np.sqrt(5) / np.pi) * (
        1 - x ** 2.0 / 5.0
    ) * np.log(np.abs((np.sqrt(5) - x) / (np.sqrt(5) + x)))
    # % Equation(4.8)
    boolean_mask = np.abs(x) == np.sqrt(5)
    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            if boolean_mask[i][j]:
                Hftemp[i][j] = (-3 / 10 / np.pi) * x[i][j]
    Hftilde = np_mean(Hftemp / H, 1)
    if p <= n:
        dtilde = lam / (
            (np.pi * (p / n) * lam * ftilde) ** 2
            + (1 - (p / n) - np.pi * (p / n) * lam * Hftilde) ** 2
        )

    #     % Equation(4.3)
    else:
        Hftilde0 = (
            (1 / np.pi)
            * (
                3 / 10.0 / h ** 2
                + 3
                / 4.0
                / np.sqrt(5)
                / h
                * (1 - 1 / 5.0 / h ** 2)
                * np.log((1 + np.sqrt(5) * h) / (1 - np.sqrt(5) * h))
            )
            * np.mean(1 / lam)
        )
        # % Equation(C.8)
        dtilde0 = 1 / (np.pi * (p - n) / n * Hftilde0)
        # % Equation(C.5)
        dtilde1 = lam / (np.pi ** 2 * lam ** 2.0 * (ftilde ** 2 + Hftilde ** 2))
        # % Eq. (C.4)
        dtilde = np.concatenate((dtilde0 * np.ones((p - n)), dtilde1))

    sigmatilde = np.dot(np.dot(u, np.diag(dtilde)), u.T)

    return sigmatilde


@njit
def prial(sample, sigma_hat, sigma):
    """Percentage Relative Improvement in Average Loss

    Args:
        sample (`numpy.ndarray`): Sample covariance
        sigma_hat (`numpy.ndarray`): Estimated Covariance
        sigma (`numpy.ndarray`): True Covariance

    Returns:
        float: Percentage improvement (between 0,1)
    """
    num = loss_mv(sample, sigma) - loss_mv(sigma_hat, sigma)
    denom = loss_mv(sample, sigma) - loss_mv(fsopt(sample, sigma), sigma)
    return num / float(denom)


@njit
def fsopt(sample, sigma):
    lam, u = np.linalg.eigh(sample)
    d_start = (np.multiply(u, np.dot(sigma, u))).sum(axis=0)
    ud = np.dot(u, np.diag(d_start))

    return np.dot(ud, u.T)


@njit
def loss_mv(sigma_hat, sigma):
    n, p = sigma.shape
    omega_hat = np.linalg.inv(sigma_hat)
    num = np.trace(np.dot(np.dot(omega_hat, sigma), omega_hat)) / p
    denom = (np.trace(omega_hat) / p) ** 2
    alpha = np.trace(np.linalg.inv(sigma)) / p
    return num / denom - alpha


@njit
def loss_fr(sigma_hat, sigma):
    n, p = sigma.shape
    delta = sigma_hat - sigma
    # return np.trace(np.dot(delta.T, delta)) / p
    return np.trace(delta ** 2) / p
