# LAYER_CONF_VERSION is increased each time build/conf/bblayers.conf
# changes incompatibly
LCONF_VERSION = "5"

BBPATH = "${TOPDIR}"
BBFILES ?= ""

BBLAYERS ?= " \
@[for layer in layers]  @layer \
@[end for]  @oe_layer \
  "

BBLAYERS_NON_REMOVABLE ?= " \
  @oe_layer \
  "
