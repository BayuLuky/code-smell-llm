def __enter__(self):
    from scrapy.utils.test import get_testenv

    pargs = [sys.executable, "-u", "-m", "scrapy.utils.benchserver"]
    self.proc = subprocess.Popen(pargs, stdout=subprocess.PIPE, env=get_testenv())
    self.proc.stdout.readline()
