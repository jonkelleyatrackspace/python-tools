# This is elegant
# http://amoffat.github.io/sh/#basic-features

import sh
run = sh.Command("/bin/uname")

print run()

print run('-p')
