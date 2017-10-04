# -*- encoding: utf8 -*-
# © Toons

from .. import rest
from .. import cfg

network = rest.GET.api.loader.autoconfigure(returnKey="network")
cfg.headers["version"] = network.pop("version")
cfg.headers["nethash"] = network.pop("nethash")
cfg.__dict__.update(network)
