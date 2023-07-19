import util.parsers.traces as parser

p = parser.TracesParserClass()

out_fname_template = "traces"
if p.args.cores != 0: out_fname_template += "_core{}"
if p.args.warps != 0: out_fname_template += "_warp{}"
out_fname_template += ".log"

# This script does not output memory requests
for i in range(p.args.cores):
    for j in range(p.args.warps):
        out_fname = out_fname_template.format(i, j)
        with open(p.args.trace_file, "r") as fin, open(p.args.output_dir+out_fname, "w") as fout:
            DEBUG_SECTION = False
            STORE = False
            for line in fin:
                if line.startswith("DEBUG ")and not DEBUG_SECTION:
                    if ("coreid={}".format(i) in line) and ("wid={}".format(j) in line): # use ad hoc function
                        DEBUG_SECTION = True
                        STORE = True
                if DEBUG_SECTION:
                    if line.startswith("TRACE "):
                        DEBUG_SECTION = False
                        STORE = False
                if not DEBUG_SECTION: 
                    if ("coreid={}".format(i) in line) and ("wid={}".format(j) in line): STORE = True # use ad hoc function
                    else: STORE = False
                if STORE: fout.write(line)
