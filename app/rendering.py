import os
import subprocess
from collections import namedtuple
from session import Session

COMPILERS = ['xelatex', 'pdflatex']

RenderResult = namedtuple('RenderResult', 'success product log')


def render_latex(session: Session) -> RenderResult:
    if session.compiler not in COMPILERS:
        raise ValueError(f"compiler '{session.compiler}' not supported")

    command = [session.compiler,
               "-interaction=nonstopmode",
               f"-jobname={session.key}",
               session.target]

    # I'm not sure how many times a latex compiler should reasonably have to run in order to handle
    # a complex case, so I've conservatively set it to time out at 5
    run_count = 0
    expected_log = None     # prevent linting ref-before-assignment warning
    while run_count < 5:
        # Run the compiler
        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, cwd=session.directory)
        process.wait()
        run_count += 1

        # Check the log file to determine if a re-run is necessary
        expected_log = os.path.join(session.directory, f"{session.key}.log")
        with open(expected_log, "r") as handle:
            if "Rerun" not in handle.read():
                break

    expected_product = os.path.join(session.directory, f"{session.key}.pdf")

    if os.path.exists(expected_product):
        return RenderResult(success=True, product=expected_product, log=expected_log)
    else:
        return RenderResult(success=False, product=None, log=expected_log)

