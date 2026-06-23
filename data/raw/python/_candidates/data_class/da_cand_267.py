class HalfTweedieLossIdentity(BaseLoss):
    """Half Tweedie deviance loss with identity link, for regression.

    Domain:
    y_true in real numbers for power <= 0
    y_true in non-negative real numbers for 0 < power < 2
    y_true in positive real numbers for 2 <= power
    y_pred in positive real numbers for power != 0
    y_pred in real numbers for power = 0
    power in real numbers

    Link:
    y_pred = raw_prediction

    For a given sample x_i, half Tweedie deviance loss with p=power is defined
    as::

        loss(x_i) = max(y_true_i, 0)**(2-p) / (1-p) / (2-p)
                    - y_true_i * raw_prediction_i**(1-p) / (1-p)
                    + raw_prediction_i**(2-p) / (2-p)

    Note that the minimum value of this loss is 0.

    Note furthermore that although no Tweedie distribution exists for
    0 < power < 1, it still gives a strictly consistent scoring function for
    the expectation.
    """

    def __init__(self, sample_weight=None, power=1.5):
        super().__init__(
            closs=CyHalfTweedieLossIdentity(power=float(power)),
            link=IdentityLink(),
        )
        if self.closs.power <= 0:
            self.interval_y_true = Interval(-np.inf, np.inf, False, False)
        elif self.closs.power < 2:
            self.interval_y_true = Interval(0, np.inf, True, False)
        else:
            self.interval_y_true = Interval(0, np.inf, False, False)

        if self.closs.power == 0:
            self.interval_y_pred = Interval(-np.inf, np.inf, False, False)
        else:
            self.interval_y_pred = Interval(0, np.inf, False, False)
