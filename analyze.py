#!/usr/bin/python

"""analyze.py

Run an analysis of a directory of non-translated ("O") and
translated ("T") files. Analysis will be performed based on
selected properties and output to stdout in ARFF format, suitable
for use with weka."""

import os
import sys
import translationese
import time
import pkgutil
import logging
from translationese import MissingVariant
import StringIO

class Timer:
    """Simple progress reporter. Call ``increment`` for every event
    which occurs, and every ``report_every`` seconds the count and
    average time will be displayed."""

    def __init__(self, report_every=1, stream=sys.stderr):
        self.report_every = report_every
        self.stream = stream

        self.started_at = 0
        self.count = 0
        self.prevtime = 0

    def start(self):
        """[re-]start the timer"""
        self.started_at = time.time()
        self.prevtime = self.started_at
        self.count = 0

    def output(self):
        elapsed = time.time() - self.started_at
        average_ms = 1000.0 * (elapsed / self.count)
        if self.stream:
            self.stream.write(\
                    "\r[%5d] %d seconds elapsed, (%.2f ms each)" \
                    % (self.count, elapsed, average_ms))
            self.stream.flush()

    def increment(self):
        """Report an event as having occured."""
        self.count += 1
        if time.time() - self.prevtime > self.report_every:
            self.output()
            self.prevtime = time.time()

    def stop(self):
        """Stop the timer, properly formatting end-of-line."""
        self.output()
        if self.stream:
            self.stream.write("\n")

def analyze_file(filename, analyzer_module, variant=None):
    with translationese.Analysis(filename=filename) as analysis:
        if variant is not None:
            return analyzer_module.quantify_variant(analysis, variant)
        else:
            return analyzer_module.quantify(analysis)

def analyze_directory(dir_to_analyze, expected_class, analyzer_module,
                      variant, timer):
    results = []

    for filename in sorted(os.listdir(dir_to_analyze)):
        if filename.endswith(".analysis"):
            # This is a cached analysis, skip it.
            continue
        filename = os.path.join(dir_to_analyze, filename)
        try:
            result = analyze_file(filename, analyzer_module, variant)
            timer.increment()
        except:
            logging.error("Error analyzing file %s", filename)
            raise

        results.append((result, expected_class))

    return results

def print_results(results, stream, timer):
    attributes = set()

    print >> stream, "@relation translationese"

    logging.info("Merging result keys")
    for result, _ in results:
        attributes.update(result.keys())

    attributes = list(attributes)
    attributes.sort()

    for attribute in attributes:
        print >> stream, "@attribute %s numeric" % repr(attribute)

    # Class attribute should be last, as this is the weka default.
    print >> stream, "@attribute class { T, O }"
    print >> stream
    print >> stream, "@data"

    logging.info("Printing results")

    timer.start()
    for result, expected_class in results:
        line = ",".join([str(result.get(x, 0)) for x in attributes])

        print >> stream, "%s,%s" % (line, expected_class)
        timer.increment()
    timer.stop()

def main(analyzer_module, o_dir, t_dir, stream=sys.stdout, variant=None,
         timer_stream=sys.stdout):
    """Internal, testable main() function for analysis."""
    if variant is None:
        if not hasattr(analyzer_module, "quantify"):
            raise MissingVariant("%s requires a variant to be specified" % \
                                 analyzer_module.__name__)
    elif not hasattr(analyzer_module, "quantify_variant"):
        raise translationese.NoVariants("%s does not support variants" % \
                                        analyzer_module.__name__)

    timer = Timer(stream=timer_stream)

    results = []

    logging.info("Analyzing 'O' directory %s", o_dir)
    timer.start()
    results += analyze_directory(o_dir, "O", analyzer_module, variant, timer)
    timer.stop()

    logging.info("Analyzing 'T' directory %s", t_dir)
    timer.start()
    results += analyze_directory(t_dir, "T", analyzer_module, variant, timer)
    timer.stop()

    print_results(results, stream, timer)

def import_translationese_module(module_name):
    return __import__('translationese.%s' % module_name,
                      fromlist='translationese')

def module_proper_name(module_name):
    """If ``module_name`` is an ordinarily quantifiable module, returns it
    as-is. If it requires a variant, ``module_name*`` is returned. If it is
    not quantifiable, ``None`` is returned."""

    module = import_translationese_module(module_name)

    if hasattr(module, 'quantify'):
        return module_name
    elif hasattr(module, 'quantify_variant'):
        return '%s*' % module_name
    else:
        return None

def available_modules():
    iterator = pkgutil.iter_modules(['translationese'])
    available_modules = (module_proper_name(x[1]) for x in iterator)
    return ' '.join(filter(None, available_modules))

def get_output_stream(outfile, variant, module_name):
    if not outfile:
        if variant is None:
            outfile = "%s.arff" % module_name
        else:
            outfile = "%s_%d.arff" % (module_name, variant)

    outstream = open(outfile, "w")

    return outstream

def cmdline_main():
    """External main() function for calling from commandline."""
    from argparse import ArgumentParser

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)-15s [%(levelname)-6s] %(message)s')

    description = '''
    Run a translationese analysis of T_DIR and O_DIR, using MODULE. Output
    is in weka-compatible ARFF format.
    '''

    epilog = '''
    VARIANT is required for modules marked with '*'. VARIANTS are 0-indexed.
    By default, OUTFILE is MODULE_NAME.arff, with an added variant number if
    present (e.g. MODULE_NAME_1.arff).
    '''

    parser = ArgumentParser(description=description, epilog=epilog)
    parser.add_argument('module', type=str, metavar='MODULE',
                        help='Available modules: %s' % available_modules())
    parser.add_argument("-v", "--variant", dest="variant", default=None,
                        type=int, help="Variant for analysis module")
    parser.add_argument("-t", dest="t_dir", default='./t/',
                        help="Directory of T (translated) texts " \
                             "[default: %(default)s]")
    parser.add_argument("-o", dest="o_dir", default='./o/',
                        help="Directory of O (original) texts " \
                             "[default: %(default)s]")
    parser.add_argument("--outfile", dest="outfile",
                        help="Write output to OUTFILE.")

    args = parser.parse_args()

    module = import_translationese_module(args.module)

    for dir_path in args.t_dir, args.o_dir:
        if not os.path.isdir(dir_path):
            parser.error("No such directory %r (run with --help)" % dir_path)

    outfile = get_output_stream(args.outfile, args.variant, args.module)

    logging.info("Output will be written to %s", outfile.name)
    main(module, o_dir=args.o_dir, t_dir=args.t_dir,
         variant=args.variant, stream=outfile)

if __name__ == '__main__':
    cmdline_main()
