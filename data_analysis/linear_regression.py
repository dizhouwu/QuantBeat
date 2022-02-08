import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.base import BaseEstimator, RegressorMixin
from cvxopt import matrix, solvers
import pandas as pd

class ConvexLinearModel(BaseEstimator, RegressorMixin):
    def __init__(self, show_progress=False):
        self.show_progress = show_progress

    def fit(self, X, y):
        n, p = X.shape
        Xt = X.T
        P = matrix(np.dot(Xt, X))
        q = -matrix(np.dot(Xt, y))
        self.coef_ = np.asarray(solvers.qp(P, q, options={
                                "show_progress": self.show_progress})['x']).T[0]
        return self

    def predict(self, X):
        return np.dot(X, self.coef_)

    def fit_predict(self, X, y):
        return self.fit(X, y).predict(X)
      
data = pd.DataFrame( {"x": np.random.normal(0,0.1,100)})
data.insert(0, "const", np.ones(len(data)))
data.insert(0, "Y", 2 * data['x'] + np.random.normal(0, 0.01, 100))

X_cols = data.columns[1:]
cvx_lm = ConvexLinearModel(False)

y_hat = cvx_lm.fit_predict(data.iloc[:,1:], data.iloc[:,0])

lr = LinearRegression(fit_intercept=True).fit(data.iloc[:,2:], data.iloc[:,0])

q, r = np.linalg.qr(data.iloc[:,1:])
scipy.linalg.solve_triangular(r, q.T.dot(data.iloc[:,0]))
y_hat2 = lr.predict(data.iloc[:,2:])


np.allclose(y_hat, y_hat2)

cvx_lm.coef_
lr.intercept_, lr.coef_[0]
