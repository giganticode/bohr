class Profiler:
    def __init__(self, enabled: bool):
        self.enabled = enabled
        if self.enabled:
            import cProfile

            self.profiler = cProfile.Profile()

    def __enter__(self):
        if self.enabled:
            self.profiler.enable()

    def __exit__(self, type, value, traceback):
        if self.enabled:
            self.profiler.disable()
            self.profiler.print_stats(sort="cumtime")
