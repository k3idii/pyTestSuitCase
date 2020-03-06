import argparse
import os
import yaml
import json
import re


VERSION="0.1-poc"

#Yup, that is global scpe :-(
AVAILABLE_FORMATS = dict()

def register_format(short_name, description):
  """ Decorator for classes used to parse input file. """
  def _prox(a):
    AVAILABLE_FORMATS[short_name] = dict(
      description=description,
      target=a
    )
    return a
  return _prox

class InputFileParser(object):
  """ Interface class """
  def __init__(self, filename, options=None):
    self.filename = filename
    self.options = options
    self.prepare()
  
  def prepare(self):
    pass # overload me 

  def produce_targets(self):
    return []

@register_format('flat', "Flat file. One entry per line. No special parsing/format.")
class FlatFileParser(InputFileParser):
  def produce_targets(self):
    for row in open(self.filename, 'r'):
      yield row

@register_format("json", "JSON file. Must contain iterable collecttion in main scope.")
class JsonFileParser(InputFileParser):
  def produce_targets(self):
    for entry in json.load(open(self.filename, 'r')):
      yield row


@register_format("yaml", "YAML file. Must contain iterable collecttion in main scope.")
class YamlFileParser(InputFileParser):
  def produce_targets(self):
    for entry in yaml.load(open(self.filename, 'r')):
      yield row

@register_format("regex", "Usage: regex:expression. Flat text file, regexp applied to each line. Kinda grep ;-)")
class RegexFileParser(InputFileParser):
  def produce_targets(self):
    rex = re.compile(self.options)
    for row in open(self.filename, 'r'):
      for match in rex.finditer(row.strip()):
        #print(row, match)
        yield(match.group(0))




class TheRunmeMachine(object):
  '''Holds configuration for tests'''
  def __init__(self, config):
    self.config = config
    print(config)

  def iterate_over_targets(self, iterable):
    for target in iterable:
      self.run_on_target(target)

  def run_on_target(self, target): # target is a String !
    for case in self.config['cases']:
      print(case, target)
  

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--version', action='version', version=VERSION)

  #subparser = parser.add_subparsers(help="Action", dest="command")
  #subopt = subparser.add_parser("list", help="List available formats (for --format)")
  #subopt = subparser.add_parser("run", help="Run test fomr [confing] on [targtes] (see run -h for help)")

  parser.add_argument("--config", help="Configuration file name")
  parser.add_argument("--output", help="Output file name.", default="report.yaml", dest="out_file")
  parser.add_argument("--load",   help="Load targets from file. Use --format to specify format.", default=None, dest="source_file")
  parser.add_argument("--format", help="Specify file format. Syntax: [format:options]. Use '?' as argument to get list", default="flat")
  parser.add_argument("--target", help="Add target to target list. Can be used multiple times. Will be tested in order, before targets loaded from file (if provided)", action="append", dest="targets", default=[])  
  
  #grp = parser.add_mutually_exclusive_group(required=True)
  #grp.add_argument("--list-formats", help="List available file formats", action="store_true", default=False, dest="show_formats")
  #grp.add_argument("--load",   help="Load targets from file. Use --format to specify format.", default=None, dest="source_file")
  #subgrp = grp.add_argument_group()
 

  args = parser.parse_args()

  if args.format == '?':
    print("Available formats:")
    for name, val in AVAILABLE_FORMATS.items():
      print(" * {name:10s} : {description}".format(name=name, **val))
    return

  def _target_generator():
    if len(args.targets)>0:
      print(">>> ARG targets")
      for x in args.targets:
        yield x
    if args.source_file is not None: 
      print(">>> Input file")
      fmt_name, opts = args.format, None,
      if ":" in fmt_name:
        fmt_name, opts = fmt_name.split(":",1)
      handler = AVAILABLE_FORMATS.get(fmt_name, None)
      assert handler is not None, "No such format !"
      fmt_obj = handler['target'](args.source_file, options=opts)
      for x in fmt_obj.produce_targets():
        yield x

  if len(args.targets) == 0 and args.source_file is None:
    print("WARNING:\n  target list empty. User --target or --load to fix that :-) \n\n")
    return

  if args.config is None:
    print("WARNING:\n  you did not provide case config file. Use --config to fix that :-) \n\n")
    return

  conf = yaml.full_load(open(args.config, 'r').read())
  machine = TheRunmeMachine(conf)
  machine.iterate_over_targets(_target_generator())

  #for target in item_generator():
  #  machine.run_on_target(target)



if __name__ == '__main__':
  main()