# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re

import invoke


REQUIREMENTS_IN = """

-f https://github.com/benoitc/gunicorn/archive/master.zip#egg=gunicorn-19.4.dev

-e .

gevent>=1.1a1
gunicorn>=19.4.dev
setproctitle
"""


REQUIREMENTS_HEADER = """
#
# This file is autogenerated by pip-compile
# Make changes in setup.py, then run this to update:
#
#    $ invoke pip.compile
#

-f https://github.com/benoitc/gunicorn/archive/master.zip#egg=gunicorn-19.4.dev

# This is handled manually, to adjust it edit tasks/pip.py and then rerun the
# pip.compile task.
pypi-theme==1.7

""".lstrip()


@invoke.task
def compile():
    with open("requirements.in", "w") as fp:
        fp.write(REQUIREMENTS_IN)

    try:
        invoke.run("pip-compile --no-header requirements.in", hide="out")
    finally:
        os.remove("requirements.in")

    lines = [REQUIREMENTS_HEADER]
    with open("requirements.txt", "r") as fp:
        for line in fp:
            # The boto3 wheel includes a futures==2.2.0 even though that is a
            # Python 2 only dependency. This dependency comes by default on
            # Python 3, so the backport is never needed. See boto/boto3#163.
            if re.search(r"^futures==2\.2\.0", line.strip()) is not None:
                continue

            if re.search(r"^-e file:///.+/warehouse$", line.strip()) is None:
                lines.append(line)

    with open("requirements.txt", "w") as fp:
        for line in lines:
            fp.write(line)
