scifig
======

scifig is a build tool for scientific figures but it could probably be used for non-scientific figures too.

This code basically defines rules to convert sources to final formats such as pdf, eps, svg, etc.
Some rules are defined for gnuplot or tikz figures for examples, but other rules can be defined, it should be easy to do so.

In few words, the idea is to drop your sources in a directory, the tool builds them in various formats and export the ready-to-use files in a directory. Each time you drop a new figure or you make edits, scifig works only on what needs to be rebuild.

It should provide:

* less file manipulations (formats, name...)
* more reproducibility
* source versioning
* automatic translations

This code is a rewritten version of a previous code named SciFigWorkflow. This tool was based on waf. The idea was to use a solid codebase, but it was difficult to maintain and to provide new evolutions to the workflow.
