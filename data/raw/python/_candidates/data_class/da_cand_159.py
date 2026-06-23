class VerboseReporter:
    """Reports verbose output to stdout.

    Parameters
    ----------
    verbose : int
        Verbosity level. If ``verbose==1`` output is printed once in a while
        (when iteration mod verbose_mod is zero).; if larger than 1 then output
        is printed for each update.
    """

    def __init__(self, verbose):
        self.verbose = verbose

    def init(self, est, begin_at_stage=0):
        """Initialize reporter

        Parameters
        ----------
        est : Estimator
            The estimator

        begin_at_stage : int, default=0
            stage at which to begin reporting
        """
        # header fields and line format str
        header_fields = ["Iter", "Train Loss"]
        verbose_fmt = ["{iter:>10d}", "{train_score:>16.4f}"]
        # do oob?
        if est.subsample < 1:
            header_fields.append("OOB Improve")
            verbose_fmt.append("{oob_impr:>16.4f}")
        header_fields.append("Remaining Time")
        verbose_fmt.append("{remaining_time:>16s}")

        # print the header line
        print(("%10s " + "%16s " * (len(header_fields) - 1)) % tuple(header_fields))

        self.verbose_fmt = " ".join(verbose_fmt)
        # plot verbose info each time i % verbose_mod == 0
        self.verbose_mod = 1
        self.start_time = time()
        self.begin_at_stage = begin_at_stage

    def update(self, j, est):
        """Update reporter with new iteration.

        Parameters
        ----------
        j : int
            The new iteration.
        est : Estimator
            The estimator.
        """
        do_oob = est.subsample < 1
        # we need to take into account if we fit additional estimators.
        i = j - self.begin_at_stage  # iteration relative to the start iter
        if (i + 1) % self.verbose_mod == 0:
            oob_impr = est.oob_improvement_[j] if do_oob else 0
            remaining_time = (
                (est.n_estimators - (j + 1)) * (time() - self.start_time) / float(i + 1)
            )
            if remaining_time > 60:
                remaining_time = "{0:.2f}m".format(remaining_time / 60.0)
            else:
                remaining_time = "{0:.2f}s".format(remaining_time)
            print(
                self.verbose_fmt.format(
                    iter=j + 1,
                    train_score=est.train_score_[j],
                    oob_impr=oob_impr,
                    remaining_time=remaining_time,
                )
            )
            if self.verbose == 1 and ((i + 1) // (self.verbose_mod * 10) > 0):
                # adjust verbose frequency (powers of 10)
                self.verbose_mod *= 10
